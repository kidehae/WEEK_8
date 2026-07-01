# api/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChannelActivityResponse(BaseModel):
    channel_name: str
    channel_type: str
    total_posts: int
    avg_views: float

    class Config:
        from_attributes = True

class MessageSearchResponse(BaseModel):
    message_id: str
    channel_key: str
    message_text: Optional[str]
    views_count: Optional[int]
    forwards_count: Optional[int]

    class Config:
        from_attributes = True

class VisualStatResponse(BaseModel):
    channel_name: str
    image_category: str
    total_images: int
    avg_confidence: float

    class Config:
        from_attributes = True