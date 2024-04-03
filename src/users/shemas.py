from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Profile(BaseModel):
    profile_id: int
    user_id: int
    full_name: str
    photo_url: Optional[str] = None
