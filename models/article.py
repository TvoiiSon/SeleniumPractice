from pydantic import BaseModel
from models.user import User
from datetime import datetime

class Article(BaseModel):
    author: User
    id: int
    title: str
    subtitle: str | None = None
    text: str
    tags: list
    image_path: str | None = None
    comments_count: int
    created_at: datetime

class Comment(BaseModel):
    author: User
    id: int
    text: str
    created_at: datetime
