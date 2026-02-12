from datetime import datetime
from pydantic import BaseModel

from app.models.feedback import FeedbackStatus, FeedbackCategory


class FeedbackCreate(BaseModel):
    title: str
    description: str = ""
    category: FeedbackCategory = FeedbackCategory.FEATURE
    author_email: str | None = None
    author_name: str = "Anonymous"


class FeedbackUpdateStatus(BaseModel):
    status: FeedbackStatus


class FeedbackResponse(BaseModel):
    id: str
    title: str
    description: str
    status: FeedbackStatus
    category: FeedbackCategory
    vote_count: int
    author_email: str | None
    author_name: str | None
    board_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VoteRequest(BaseModel):
    voter_email: str | None = None
