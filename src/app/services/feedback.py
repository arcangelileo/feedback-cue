from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import FeedbackItem, FeedbackStatus, FeedbackCategory
from app.models.vote import Vote


async def create_feedback(
    db: AsyncSession,
    board_id: str,
    title: str,
    description: str,
    category: FeedbackCategory,
    author_email: str | None,
    author_name: str,
) -> FeedbackItem:
    item = FeedbackItem(
        board_id=board_id,
        title=title,
        description=description,
        category=category,
        author_email=author_email,
        author_name=author_name,
    )
    db.add(item)
    await db.flush()
    return item


async def get_feedback_for_board(
    db: AsyncSession,
    board_id: str,
    status: FeedbackStatus | None = None,
    category: FeedbackCategory | None = None,
    sort_by: str = "votes",
) -> list[FeedbackItem]:
    query = select(FeedbackItem).where(FeedbackItem.board_id == board_id)

    if status:
        query = query.where(FeedbackItem.status == status)
    if category:
        query = query.where(FeedbackItem.category == category)

    if sort_by == "newest":
        query = query.order_by(FeedbackItem.created_at.desc())
    elif sort_by == "oldest":
        query = query.order_by(FeedbackItem.created_at.asc())
    else:  # votes (default)
        query = query.order_by(FeedbackItem.vote_count.desc(), FeedbackItem.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_feedback_by_id(db: AsyncSession, item_id: str) -> FeedbackItem | None:
    result = await db.execute(select(FeedbackItem).where(FeedbackItem.id == item_id))
    return result.scalar_one_or_none()


async def update_feedback_status(db: AsyncSession, item: FeedbackItem, status: FeedbackStatus) -> FeedbackItem:
    item.status = status
    await db.flush()
    return item


async def toggle_vote(db: AsyncSession, item_id: str, voter_id: str, voter_email: str | None = None) -> bool:
    """Toggle vote on a feedback item. Returns True if vote was added, False if removed."""
    result = await db.execute(
        select(Vote).where(Vote.feedback_item_id == item_id, Vote.voter_id == voter_id)
    )
    existing_vote = result.scalar_one_or_none()

    item = await get_feedback_by_id(db, item_id)
    if item is None:
        return False

    if existing_vote:
        await db.delete(existing_vote)
        item.vote_count = max(0, item.vote_count - 1)
        await db.flush()
        return False
    else:
        vote = Vote(
            feedback_item_id=item_id,
            voter_id=voter_id,
            voter_email=voter_email,
        )
        db.add(vote)
        item.vote_count += 1
        await db.flush()
        return True


async def has_voted(db: AsyncSession, item_id: str, voter_id: str) -> bool:
    result = await db.execute(
        select(Vote).where(Vote.feedback_item_id == item_id, Vote.voter_id == voter_id)
    )
    return result.scalar_one_or_none() is not None
