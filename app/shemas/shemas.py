from pydantic import BaseModel
from datetime import datetime

class PlaylistSchema(BaseModel):
    user_id: int
    title:str
    
class FavoritesShema(BaseModel):
    user_id: int
    track_id: int
