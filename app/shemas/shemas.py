from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PlaylistSchema(BaseModel):
    user_id: int
    title:str
    
class FavoritesShema(BaseModel):
    user_id: int
    track_id: int

class ListeningHistoryShema(BaseModel):
    user_id: int
    track_id: int
    play_duraction: int
    
class TrackResponse(BaseModel):
    id: int
    title: str
    file_url: str
    duration: int
    artist_name: Optional[str] = None  # Вместо artist_id
    created_at: datetime

    class Config:
        from_attributes = True  # Позволяет создавать модель из ORM объектов