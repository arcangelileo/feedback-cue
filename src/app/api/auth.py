from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import UserRegister, UserLogin
from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_user_by_email,
    get_user_by_username,
    register_user,
)
from app.api.deps import get_current_user, get_optional_user
from app.models.user import User

router = APIRouter(tags=["auth"])

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse(request, "auth/register.html")


@router.post("/register")
async def register(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    form = await request.form()
    email = form.get("email", "").strip()
    username = form.get("username", "").strip()
    password = form.get("password", "")

    errors = []
    if not email:
        errors.append("Email is required")
    if not username:
        errors.append("Username is required")
    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters")

    if not errors:
        existing_email = await get_user_by_email(db, email)
        if existing_email:
            errors.append("Email already registered")
        existing_username = await get_user_by_username(db, username)
        if existing_username:
            errors.append("Username already taken")

    if errors:
        return templates.TemplateResponse(
            request,
            "auth/register.html",
            {"errors": errors, "email": email, "username": username},
            status_code=422,
        )

    user = await register_user(db, email, username, password)
    token = create_access_token(user.id)
    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie("access_token", token, httponly=True, max_age=60 * 60 * 24, samesite="lax")
    return response


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse(request, "auth/login.html")


@router.post("/login")
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    form = await request.form()
    email = form.get("email", "").strip()
    password = form.get("password", "")

    user = await authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"errors": ["Invalid email or password"], "email": email},
            status_code=401,
        )

    token = create_access_token(user.id)
    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie("access_token", token, httponly=True, max_age=60 * 60 * 24, samesite="lax")
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response


# API endpoints for JSON clients
@router.post("/api/auth/register", status_code=201)
async def api_register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    user = await register_user(db, data.email, data.username, data.password)
    token = create_access_token(user.id)
    return {"user": {"id": user.id, "email": user.email, "username": user.username}, "token": token}


@router.post("/api/auth/login")
async def api_login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id)
    return {"user": {"id": user.id, "email": user.email, "username": user.username}, "token": token}
