from fastapi import FastAPI, HTTPException, Depends
from authx import AuthX, AuthXConfig

from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from pydantic import BaseModel

# from models.shemas import UserSchema
# from models.models import *

from routes.tracks import router as tracks_router
from routes.artists import router as artist_router
from routes.auth import router as auth_router
from routes.playlists import router as playlists_router
from routes.history import router as history_router

from fastapi.middleware.cors import CORSMiddleware

import uvicorn

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tracks_router)
app.include_router(artist_router)
app.include_router(auth_router)
app.include_router(playlists_router)
app.include_router(history_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)