from authx import AuthX, AuthXConfig

from fastapi import APIRouter, Request, HTTPException, Depends,status, Response
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from typing import Annotated

from core.config import settings
from models.models import UsersModel


from pydantic import BaseModel

DATABASE_URL = settings.database_url
config = AuthXConfig()
config.JWT_SECRET_KEY = settings.jwt_secret_key
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_SECURE = False   # ❗ для localhost
config.JWT_COOKIE_SAMESITE = "lax" # или "none"
config.JWT_COOKIE_CSRF_PROTECT = False

security = AuthX(config=config)

router = APIRouter()

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # отключить лог SQL в консоли 
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

class UserLoginShema(BaseModel):
    username: str
    email:str
    password:  str
    
@router.post("/register")
async def register(user: UserLoginShema, session: SessionDep, response: Response):
    result = await session.execute(select(UsersModel).where(UsersModel.username == user.username))
    if not result.scalar_one_or_none():
        try:
            db_user = UsersModel(
                username=user.username,
                email=user.email,
                password_hash=user.password
            )
            
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            return user
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await session.close()

class LoginSchema(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginSchema, session: SessionDep, response: Response):
    result = await session.execute(
        select(UsersModel).where(UsersModel.username == data.username)
    )
    user = result.scalar_one_or_none()

    if not user or data.password != user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = security.create_access_token(uid=str(user.id))

    response.set_cookie(
        key=config.JWT_ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
    )

    return {
        "user": {
            "id": user.id,
            "username": user.username
        }
    }

    
@router.get("/protected", dependencies=[Depends(security.access_token_required)])
async def protected():
    return {"message": "hello world!"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("my_access_token")
    return {"success": True}

@router.get("/me")
async def get_me(request: Request, session: SessionDep):
    try:
        token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
        if not token:
            return {"user": None}

        payload = security._decode_token(token)
        user_id = payload.get("sub") # type: ignore

        result = await session.execute(
            select(UsersModel).where(UsersModel.id == int(user_id))
        )
        user = result.scalar_one_or_none()

        if not user:
            return {"user": None}

        return {
            "user": {
                "id": user.id,
                "username": user.username
            }
        }

    except Exception:
        return {"user": None}