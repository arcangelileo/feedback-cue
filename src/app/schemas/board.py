from datetime import datetime
from pydantic import BaseModel


class BoardCreate(BaseModel):
    name: str
    description: str = ""
    accent_color: str = "#4F46E5"


class BoardUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    accent_color: str | None = None
    slug: str | None = None


class BoardResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    accent_color: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
