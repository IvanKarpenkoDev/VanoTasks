from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Profile(BaseModel):
    user_id: int
    full_name: str
    photo_url: str
