from fastapi import FastAPI, HTTPException, Depends
from authx import AuthX, AuthXConfig

from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from pydantic import BaseModel

# from models.shemas import UserSchema
# from models.models import *

from app.routes.tracks import router as tracks_router
from app.routes.artists import router as artist_router
from app.routes.auth import router as auth_router
from app.routes.playlists import router as playlists_router
from app.routes.history import router as history_router


app = FastAPI()

app.include_router(tracks_router)
app.include_router(artist_router)
app.include_router(auth_router)
app.include_router(playlists_router)
app.include_router(history_router)