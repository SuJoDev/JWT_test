from fastapi import APIRouter, Request, HTTPException, Depends

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from typing import Annotated

from app.models.models import ArtistsModel, AlbomsModel, TracksModel

from app.core.config import settings


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

@router.get("/artists")
async def get_artist(session: SessionDep):
    result = await session.execute(select(ArtistsModel))
    artists = result.scalars().all()
    return HTTPException(status_code=200, detail={"result" : artists})

@router.get("/alboms")
async def get_alboms(session: SessionDep):
    result = await session.execute(select(AlbomsModel).order_by(AlbomsModel.id))
    alboms = result.scalars().all()
    return HTTPException(status_code=200, detail={"result": alboms})

@router.get("/tracks")
async def get_tracks(session: SessionDep):
    result = await session.execute(select(TracksModel).order_by(TracksModel.id))
    tracks = result.scalars().all()
    return HTTPException(status_code=200, detail={"result": tracks})