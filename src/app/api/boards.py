from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.feedback import FeedbackStatus, FeedbackCategory
from app.api.deps import get_current_user, get_optional_user
from app.services.board import (
    create_board,
    get_boards_by_owner,
    get_board_by_slug,
    get_board_by_id,
    update_board,
    delete_board,
    get_board_stats,
)
from app.services.feedback import get_feedback_for_board
from app.schemas.board import BoardCreate, BoardResponse

router = APIRouter(tags=["boards"])

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    boards = await get_boards_by_owner(db, user.id)
    board_stats = {}
    for board in boards:
        board_stats[board.id] = await get_board_stats(db, board.id)
    return templates.TemplateResponse(
        request,
        "dashboard/boards.html",
        {"user": user, "boards": boards, "board_stats": board_stats},
    )


@router.post("/dashboard/boards")
async def create_board_form(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    form = await request.form()
    name = form.get("name", "").strip()
    description = form.get("description", "").strip()
    accent_color = form.get("accent_color", "#4F46E5").strip()

    if not name:
        boards = await get_boards_by_owner(db, user.id)
        return templates.TemplateResponse(
            request,
            "dashboard/boards.html",
            {"user": user, "boards": boards, "errors": ["Board name is required"]},
            status_code=422,
        )

    board = await create_board(db, name, description, accent_color, user.id)
    return RedirectResponse(f"/dashboard/boards/{board.id}", status_code=302)


@router.get("/dashboard/boards/{board_id}", response_class=HTMLResponse)
async def board_detail(
    request: Request,
    board_id: str,
    status_filter: str | None = None,
    category_filter: str | None = None,
    sort: str = "votes",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    board = await get_board_by_id(db, board_id)
    if not board or board.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Board not found")

    status_enum = FeedbackStatus(status_filter) if status_filter else None
    category_enum = FeedbackCategory(category_filter) if category_filter else None
    items = await get_feedback_for_board(db, board.id, status=status_enum, category=category_enum, sort_by=sort)

    return templates.TemplateResponse(
        request,
        "dashboard/board_detail.html",
        {
            "user": user,
            "board": board,
            "items": items,
            "status_filter": status_filter,
            "category_filter": category_filter,
            "sort": sort,
            "statuses": FeedbackStatus,
            "categories": FeedbackCategory,
        },
    )


@router.get("/dashboard/boards/{board_id}/settings", response_class=HTMLResponse)
async def board_settings_page(
    request: Request,
    board_id: str,
    saved: bool = False,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    board = await get_board_by_id(db, board_id)
    if not board or board.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Board not found")

    return templates.TemplateResponse(
        request,
        "dashboard/board_settings.html",
        {"user": user, "board": board, "saved": saved},
    )


@router.post("/dashboard/boards/{board_id}/settings")
async def update_board_settings(
    request: Request,
    board_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    board = await get_board_by_id(db, board_id)
    if not board or board.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Board not found")

    form = await request.form()
    name = form.get("name", "").strip()
    description = form.get("description", "").strip()
    accent_color = form.get("accent_color", board.accent_color).strip()
    slug = form.get("slug", "").strip()

    if not name:
        return templates.TemplateResponse(
            request,
            "dashboard/board_settings.html",
            {"user": user, "board": board, "errors": ["Board name is required"]},
            status_code=422,
        )

    await update_board(db, board, name=name, description=description, accent_color=accent_color, slug=slug)
    return RedirectResponse(f"/dashboard/boards/{board.id}/settings?saved=true", status_code=302)


@router.post("/dashboard/boards/{board_id}/delete")
async def delete_board_form(
    board_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    board = await get_board_by_id(db, board_id)
    if not board or board.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Board not found")

    await delete_board(db, board)
    return RedirectResponse("/dashboard", status_code=302)


@router.post("/dashboard/boards/{board_id}/feedback/{item_id}/status")
async def update_item_status(
    request: Request,
    board_id: str,
    item_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services.feedback import get_feedback_by_id, update_feedback_status

    board = await get_board_by_id(db, board_id)
    if not board or board.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Board not found")

    item = await get_feedback_by_id(db, item_id)
    if not item or item.board_id != board_id:
        raise HTTPException(status_code=404, detail="Feedback item not found")

    form = await request.form()
    new_status = form.get("status")
    if new_status:
        await update_feedback_status(db, item, FeedbackStatus(new_status))

    return RedirectResponse(f"/dashboard/boards/{board_id}", status_code=302)


# JSON API endpoints
@router.post("/api/boards", status_code=201)
async def api_create_board(
    data: BoardCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    board = await create_board(db, data.name, data.description, data.accent_color, user.id)
    return BoardResponse.model_validate(board)


@router.get("/api/boards")
async def api_list_boards(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    boards = await get_boards_by_owner(db, user.id)
    return [BoardResponse.model_validate(b) for b in boards]
