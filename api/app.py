from fastapi import FastAPI, HTTPException, Response, Depends
from authx import AuthX, AuthXConfig

from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from pydantic import BaseModel


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/Auralis"
SECRET_KEY = "secret_key"

app = FastAPI()

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

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["headers"]

security = AuthX(config=config)

from models.models import *

class UserLoginShema(BaseModel):
    username: str
    password:  str

@app.post("/login")
async def login(username: str, password: str, session: SessionDep, response: Response):
    result = await session.execute(select(UsersModel).where(UsersModel.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Асинхронная проверка пароля
    if password == user.password:
    
        token = security.create_access_token(uid=str(user.id))
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
            
        return {"access_token" : token}
    raise HTTPException(status_code=401, detail = "Incorect password or login")

    
@app.get("/protected", dependencies=[Depends(security.access_token_required)])
async def protected():
    return {"message": "hello world!"}