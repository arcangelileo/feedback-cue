import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FeedbackStatus(str, PyEnum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    SHIPPED = "shipped"
    CLOSED = "closed"


class FeedbackCategory(str, PyEnum):
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    QUESTION = "question"


class FeedbackItem(Base):
    __tablename__ = "feedback_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    status: Mapped[FeedbackStatus] = mapped_column(
        Enum(FeedbackStatus), nullable=False, default=FeedbackStatus.OPEN
    )
    category: Mapped[FeedbackCategory] = mapped_column(
        Enum(FeedbackCategory), nullable=False, default=FeedbackCategory.FEATURE
    )
    vote_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    author_email: Mapped[str] = mapped_column(String(255), nullable=True)
    author_name: Mapped[str] = mapped_column(String(100), nullable=True, default="Anonymous")
    board_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    board: Mapped["Board"] = relationship(back_populates="items")
    votes: Mapped[list["Vote"]] = relationship(
        back_populates="feedback_item", cascade="all, delete-orphan"
    )
