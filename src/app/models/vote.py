import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("feedback_item_id", "voter_id", name="uq_vote_per_voter"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    feedback_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("feedback_items.id", ondelete="CASCADE"), nullable=False
    )
    voter_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )  # session cookie ID or email
    voter_email: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    feedback_item: Mapped["FeedbackItem"] = relationship(back_populates="votes")
