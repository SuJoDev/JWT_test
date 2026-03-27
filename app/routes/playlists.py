from authx import AuthX, AuthXConfig

from fastapi import APIRouter, Request, HTTPException, Depends,status, Response
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, join

from typing import Annotated

from core.config import settings
from models.models import PlaylistsModels, TracksModel, ArtistsModel
from shemas.shemas import PlaylistSchema


from pydantic import BaseModel

DATABASE_URL = settings.database_url
config = AuthXConfig()
config.JWT_SECRET_KEY = settings.jwt_secret_key
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False

security = AuthX(config=config)

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

from datetime import datetime, timezone

async def utc_now() -> datetime:
    return datetime.now(timezone.utc)

@router.get("/{user_id}/playlists",status_code=200 ,dependencies= [Depends(security.access_token_required)])
async def get_playlists(session: SessionDep, user_id:int):
    result = await session.execute(select(PlaylistsModels).where(PlaylistsModels.user_id == user_id))
    playlists = result.scalars().all()
    return playlists

@router.post("/{user_id}/playlists/create", status_code=200, dependencies= [Depends(security.access_token_required)])
async def create_playlist(playlist: PlaylistSchema, session: SessionDep):
    time_now = await utc_now()
    try:
        db_playlist = PlaylistsModels(
            user_id = playlist.user_id,
            title = playlist.title,
            created_at = time_now
        )
        session.add(db_playlist)
        await session.commit()
        await session.refresh(db_playlist)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass
    
@router.get("/tracks",
    dependencies=[Depends(security.access_token_required)])
async def get_tracks(
    session: SessionDep):
    result = await session.execute(
        select(TracksModel.id, TracksModel.title, ArtistsModel.name)
        .join(ArtistsModel, TracksModel.artist_id == ArtistsModel.id)
    )
    return result.scalars().all()
