from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    user_id: int
    country: str
    gender: str

class Event(BaseModel):
    user_id: str
    account_type: str
    date: str
    event_type: Optional[str] = ''
    order_value: Optional[float] = None
    version: str