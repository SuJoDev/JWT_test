from fastapi import APIRouter, Request, HTTPException, Depends

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from typing import Annotated

from models.models import ArtistsModel, AlbomsModel, TracksModel
from shemas.shemas import TrackResponse

from core.config import settings


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

@router.get("/tracks", response_model=list[TrackResponse])
async def get_tracks(session: SessionDep):
    # Делаем join с таблицей Artists, чтобы получить имя
    # outerjoin используется, чтобы не потерять треки, у которых artist_id = NULL
    stmt = (
        select(TracksModel, ArtistsModel.name)
        .outerjoin(ArtistsModel, TracksModel.artist_id == ArtistsModel.id)
        .order_by(TracksModel.id)
    )
    
    result = await session.execute(stmt)
    rows = result.all() # Возвращает кортежи (TrackObject, artist_name)

    response_data = []
    for track, artist_name in rows:
        # Конвертируем ORM объект в словарь
        track_data = {c.name: getattr(track, c.name) for c in track.__table__.columns}
        
        # Заменяем artist_id на artist_name
        track_data['artist_name'] = artist_name
        track_data.pop('artist_id', None) # Удаляем ID, если не нужен
        
        response_data.append(track_data)

    return response_data
    # tracks_data = []
    # for track, artist_name in rows:
    #     # Преобразуем ORM-объект в словарь
    #     track_dict = {
    #         "id": track.id,
    #         "title": track.title,
    #         "file_url": track.file_url,
    #         "duration": track.duration,
    #         "artist_name": artist_name,  # Вместо artist_id
    #         "created_at": track.created_at,
    #         "album_id": track.album_id,
    #     }
    #     tracks_data.append(track_dict)

    # return {
    #     "status_code": 200,
    #     "detail": {
    #         "result": tracks_data
    #     },
    #     "headers": None
    # }