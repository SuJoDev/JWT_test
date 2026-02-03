import os 

from fastapi import APIRouter, Request, HTTPException, Depends,status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from fastapi.responses import StreamingResponse

from typing import Annotated

from app.core.config import settings
from app.models.models import TracksModel, FavoritiesTracks
from app.shemas.shemas import FavoritesShema


DATABASE_URL = settings.database_url
router = APIRouter()

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # отключить лог SQL в консоли (ускоряет)
    pool_size=20,  # размер пула соединений
    max_overflow=10,  # дополнительные соединения сверх пула
    pool_pre_ping=True,  # проверять соединение перед использованием
    pool_recycle=3600,  # пересоздавать соединения каждые N секунд
)
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session
        
SessionDep = Annotated[AsyncSession, Depends(get_session)]

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, "media", "tracks")
CHUNK_SIZE = 1024 * 1024 #1МБ

#сичтывание файла
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
            
async def get_track_url(session: AsyncSession, track_id: int) -> str:
    result = await session.execute(
        select(TracksModel.file_url).where(TracksModel.id == track_id)
    )
    track = result.scalar()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track with id {track_id} not found"
        )
    
    return track
            
@router.get("/tracks/{track_id}/stream")
async def stream_track(track_id: int,
                        request: Request,
                        session: SessionDep
):
    file_url = await get_track_url(session, track_id)
    
    file_path = os.path.join(MEDIA_ROOT, file_url)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Track not found")
    
    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("range")
    
    start = 0
    end = file_size - 1
    
    if range_header:
        _, range_value = range_header.split("=")
        start_str, end_str = range_value.split("-")
        start = int(start_str)
        if end_str:
            end = int(end_str)
            
    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
        "Content-Type": "audio/mpeg"
    }
    
    return StreamingResponse(
        iter_file(file_path, start, end),
        status_code=206,
        headers=headers,
    )
    
@router.post("/{user_id}/tracks/{track_id}")
async def marck_track(favorite: FavoritesShema, session: SessionDep):
    try:
        db_favorites = FavoritiesTracks(
            user_id = favorite.user_id,
            track_id = favorite.track_id
        )
        session.add(db_favorites)
        await session.commit()
        await session.refresh(db_favorites)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass