from typing import Annotated
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.models import UsersModel, Base
from security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/Auralis"
SECRET_KEY = "secret_key"

app = FastAPI()
security = HTTPBearer()

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

# ================ AUTH UTILS ================

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: SessionDep
):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    result = await session.execute(select(UsersModel).where(UsersModel.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

CurrentUser = Annotated[UsersModel, Depends(get_current_user)]

# ================ ROUTES ================

@app.post("/register")
async def register(username: str, password: str, session: SessionDep):
    # Проверка, существует ли пользователь
    result = await session.execute(select(UsersModel).where(UsersModel.username == username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Создание нового пользователя
    hashed_password = await get_password_hash(password)
    new_user = UsersModel(username=username, password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}

@app.post("/login")
async def login(username: str, password: str, session: SessionDep):
    result = await session.execute(select(UsersModel).where(UsersModel.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Асинхронная проверка пароля
    if not await verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }

@app.get("/me")
async def me(current_user: CurrentUser):
    return {
        "id": current_user.id,
        "username": current_user.username
    }