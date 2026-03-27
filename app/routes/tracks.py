import os
import mimetypes
import asyncio
import uuid
from typing import Annotated
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from core.config import settings
from models.models import TracksModel, FavoritiesTracks
from shemas.shemas import FavoritesShema

DATABASE_URL = settings.database_url

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
TRACKS_DIR = os.path.join(MEDIA_ROOT, "tracks")
COVERS_DIR = os.path.join(MEDIA_ROOT, "covers")

os.makedirs(TRACKS_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

CHUNK_SIZE = 1024 * 1024  # 1мб

router = APIRouter()



async def get_track_from_db(session: AsyncSession, track_id: int) -> TracksModel:
    track = await session.get(TracksModel, track_id)
    if not track:
        raise HTTPException(status_code=404, detail=f"Track with id {track_id} not found")
    return track

def iter_file(path: str, start: int, end: int):
    with open(path, "rb") as file:
        file.seek(start)
        remaining = end - start + 1
        
        while remaining > 0:
            chunk = file.read(min(CHUNK_SIZE, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk

async def iter_file_async(path: str, start: int, end: int):
    loop = asyncio.get_event_loop()

    def read_chunks():
        with open(path, "rb") as file:
            file.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = file.read(min(CHUNK_SIZE, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
   
    for chunk in await loop.run_in_executor(None, lambda: list(read_chunks())):
        yield chunk


@router.get("/tracks/{track_id}/stream")
async def stream_track(
    track_id: int,
    request: Request,
    session: SessionDep
):
    track = await get_track_from_db(session, track_id)
    
    file_name = track.file_url
    file_path = os.path.join(TRACKS_DIR, file_name)
    
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found on server")
    
    if not os.path.abspath(file_path).startswith(os.path.abspath(TRACKS_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("range")
    
    start = 0
    end = file_size - 1
    status_code = 200
    
    if range_header:
        try:
            range_unit, range_value = range_header.split("=")
            if range_unit.lower() == "bytes":
                start_str, end_str = range_value.split("-")
                start = int(start_str) if start_str else 0
                end = int(end_str) if end_str else file_size - 1
                end = min(end, file_size - 1)  # Защита от выхода за границы
                
                if start > end:
                    raise HTTPException(status_code=416, detail="Invalid range")
                    
                status_code = 206
        except (ValueError, IndexError):
            pass

    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or "audio/mpeg"
    
    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
        "Content-Type": content_type,
        "Content-Disposition": f"inline; filename={os.path.basename(file_path)}"
    }
    
    return StreamingResponse(
        iter_file(file_path, start, end),
        status_code=status_code,
        headers=headers,
    )

@router.get("/tracks/{track_id}/cover")
async def get_track_cover(
    track_id: int,
    session: SessionDep
):
    track = await get_track_from_db(session, track_id)
    
    if not track.img_url:
        raise HTTPException(status_code=404, detail="Cover image not found")
    
    file_path = os.path.normpath(os.path.join(COVERS_DIR, track.img_url))

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Cover file not found")
        
    if not os.path.abspath(file_path).startswith(os.path.abspath(COVERS_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")

    ext = os.path.splitext(file_path)[1].lower().lstrip('.')
    media_type = f"image/{ext}" if ext in ["jpg", "jpeg", "png", "webp", "gif"] else "image/jpeg"
    
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=31536000"}
    )

@router.post("/tracks/{track_id}/cover")
async def upload_track_cover(
    track_id: int,
    session: SessionDep,
    file: UploadFile = File(...)
):
    track = await get_track_from_db(session, track_id)
    
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(COVERS_DIR, filename)

    try:
        with open(save_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        track.img_url = filename
        await session.commit()
        
        return {
            "message": "Cover uploaded successfully",
            "cover_url": f"/api/tracks/{track_id}/cover"
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/tracks/{track_id}")
async def mark_track(
    user_id: int,
    track_id: int,
    session: SessionDep
):
    try: 
        db_favorites = FavoritiesTracks(
            user_id=user_id,
            track_id=track_id
        )
        session.add(db_favorites)
        await session.commit()
        await session.refresh(db_favorites)
        
        return {"status": "success", "favorite_id": db_favorites}
        
    except Exception as e:
        await session.rollback()
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=400, detail="Track already in favorites")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}/tracks/{track_id}")
async def remove_track_from_favorites(
    user_id: int,
    track_id: int,
    session: SessionDep
):
    try:
        result = await session.execute(
            select(FavoritiesTracks).where(
                FavoritiesTracks.user_id == user_id,
                FavoritiesTracks.track_id == track_id
            )
        )
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")
            
        await session.delete(favorite)
        await session.commit()
        
        return {"status": "deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tracks")
async def get_tracks(session: SessionDep):
    from sqlalchemy import select

    
    result = await session.execute(
        select(
            TracksModel.id,
            TracksModel.title,
            TracksModel.img_url,
            TracksModel.file_url,
        )
    )
    
    tracks = []
    for row in result.mappings():
        d = dict(row)
        d["cover_url"] = f"/tracks/{d['id']}/cover" if d.get('img_url') else None
        d["stream_url"] = f"/tracks/{d['id']}/stream"
        tracks.append(d)
    
    return tracks