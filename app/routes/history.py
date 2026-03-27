from authx import AuthX, AuthXConfig

from sqlalchemy import select

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from typing import Annotated

from core.config import settings
from models.models import ListeningHistoryModel
from shemas.shemas import ListeningHistoryShema


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

@router.get("/{user_id}/history", dependencies=[Depends(security.access_token_required)])
async def get_history(session: SessionDep, user_id: int):
    result = await session.execute(select(ListeningHistoryModel).where(ListeningHistoryModel.user_id == user_id).order_by(ListeningHistoryModel.played_at))
    history = result.scalars().all()
    return history

@router.post("/{user_id}/history/add", dependencies=[Depends(security.access_token_required)])
async def add_to_histriy(history: ListeningHistoryShema, session: SessionDep):
    try:
        db_history = ListeningHistoryModel(
        user_id = history.user_id,
        track_id = history.track_id,
        play_duration = history.play_duraction
        )
        session.add(db_history)
        await session.commit()
        await session.refresh(db_history)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass