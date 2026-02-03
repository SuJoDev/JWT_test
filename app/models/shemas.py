from pydantic import BaseModel
from datetime import date
from typing import Optional


class UserSchema(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None