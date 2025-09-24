# security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import asyncio
from functools import partial

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ================ АСИНХРОННЫЕ ФУНКЦИИ ХЕШИРОВАНИЯ ================

async def get_password_hash(password: str) -> str:
    """Асинхронно хеширует пароль (не блокирует event loop)"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(pwd_context.hash, password))

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Асинхронно проверяет пароль"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(pwd_context.verify, plain_password, hashed_password))

# ================ JWT ТОКЕНЫ ================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создаёт JWT access-токен"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Декодирует и проверяет JWT токен. Возвращает payload или None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None