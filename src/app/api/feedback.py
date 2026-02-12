from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.feedback import FeedbackStatus, FeedbackCategory
from app.api.deps import get_optional_user, get_voter_id
from app.services.board import get_board_by_slug
from app.services.feedback import (
    create_feedback,
    get_feedback_for_board,
    get_feedback_by_id,
    toggle_vote,
    has_voted,
)

router = APIRouter(tags=["feedback"])

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/b/{slug}", response_class=HTMLResponse)
async def public_board(
    request: Request,
    response: Response,
    slug: str,
    status_filter: str | None = None,
    category_filter: str | None = None,
    sort: str = "votes",
    db: AsyncSession = Depends(get_db),
):
    board = await get_board_by_slug(db, slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    user = await get_optional_user(request, db)
    voter_id = get_voter_id(request, response)

    status_enum = FeedbackStatus(status_filter) if status_filter else None
    category_enum = FeedbackCategory(category_filter) if category_filter else None
    items = await get_feedback_for_board(db, board.id, status=status_enum, category=category_enum, sort_by=sort)

    # Check which items the current voter has voted on
    voted_items = set()
    for item in items:
        if await has_voted(db, item.id, voter_id):
            voted_items.add(item.id)

    return templates.TemplateResponse(
        "public/board.html",
        {
            "request": request,
            "board": board,
            "items": items,
            "user": user,
            "voted_items": voted_items,
            "status_filter": status_filter,
            "category_filter": category_filter,
            "sort": sort,
            "statuses": FeedbackStatus,
            "categories": FeedbackCategory,
        },
    )


@router.post("/b/{slug}/submit")
async def submit_feedback(
    request: Request,
    response: Response,
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    board = await get_board_by_slug(db, slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    form = await request.form()
    title = form.get("title", "").strip()
    description = form.get("description", "").strip()
    category = form.get("category", "feature")
    author_email = form.get("author_email", "").strip() or None
    author_name = form.get("author_name", "").strip() or "Anonymous"

    if not title:
        return RedirectResponse(f"/b/{slug}", status_code=302)

    await create_feedback(
        db, board.id, title, description, FeedbackCategory(category), author_email, author_name
    )
    return RedirectResponse(f"/b/{slug}", status_code=302)


@router.post("/b/{slug}/vote/{item_id}")
async def vote_on_item(
    request: Request,
    response: Response,
    slug: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    board = await get_board_by_slug(db, slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    voter_id = get_voter_id(request, response)
    form = await request.form()
    voter_email = form.get("voter_email", "").strip() or None

    await toggle_vote(db, item_id, voter_id, voter_email)
    return RedirectResponse(f"/b/{slug}", status_code=302)
