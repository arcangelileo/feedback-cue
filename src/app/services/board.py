from slugify import slugify
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.models.feedback import FeedbackItem


async def generate_unique_slug(db: AsyncSession, name: str, exclude_id: str | None = None) -> str:
    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    while True:
        query = select(Board).where(Board.slug == slug)
        if exclude_id:
            query = query.where(Board.id != exclude_id)
        result = await db.execute(query)
        if result.scalar_one_or_none() is None:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


async def create_board(db: AsyncSession, name: str, description: str, accent_color: str, owner_id: str) -> Board:
    slug = await generate_unique_slug(db, name)
    board = Board(
        name=name,
        slug=slug,
        description=description,
        accent_color=accent_color,
        owner_id=owner_id,
    )
    db.add(board)
    await db.flush()
    return board


async def get_boards_by_owner(db: AsyncSession, owner_id: str) -> list[Board]:
    result = await db.execute(
        select(Board).where(Board.owner_id == owner_id).order_by(Board.created_at.desc())
    )
    return list(result.scalars().all())


async def get_board_by_slug(db: AsyncSession, slug: str) -> Board | None:
    result = await db.execute(select(Board).where(Board.slug == slug))
    return result.scalar_one_or_none()


async def get_board_by_id(db: AsyncSession, board_id: str) -> Board | None:
    result = await db.execute(select(Board).where(Board.id == board_id))
    return result.scalar_one_or_none()


async def update_board(db: AsyncSession, board: Board, **kwargs) -> Board:
    if "slug" in kwargs and kwargs["slug"]:
        raw_slug = kwargs.pop("slug")
        slug = await generate_unique_slug(db, raw_slug, exclude_id=board.id)
        board.slug = slug
    elif "slug" in kwargs:
        del kwargs["slug"]
    for key, value in kwargs.items():
        if value is not None:
            setattr(board, key, value)
    await db.flush()
    return board


async def delete_board(db: AsyncSession, board: Board) -> None:
    await db.delete(board)
    await db.flush()


async def get_board_stats(db: AsyncSession, board_id: str) -> dict:
    """Get feedback count and total votes for a board."""
    result = await db.execute(
        select(
            func.count(FeedbackItem.id),
            func.coalesce(func.sum(FeedbackItem.vote_count), 0),
        ).where(FeedbackItem.board_id == board_id)
    )
    row = result.one()
    return {"item_count": row[0], "total_votes": row[1]}
