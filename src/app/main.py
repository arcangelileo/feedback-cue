from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database import engine, Base, get_db, async_session
from app.api import auth, boards, feedback
from app.api.deps import get_optional_user
from app.models.user import User

settings = get_settings()

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev convenience; Alembic for production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="Customer feedback and feature request boards",
    version="0.1.0",
    lifespan=lifespan,
)

async def _handle_http_exception(request: Request, exc):
    accept = request.headers.get("accept", "")
    is_html = "text/html" in accept
    if exc.status_code == 401 and is_html:
        return RedirectResponse("/login", status_code=302)
    if exc.status_code == 404 and is_html:
        user = None
        try:
            async with async_session() as db:
                user = await get_optional_user(request, db)
        except Exception:
            pass
        return templates.TemplateResponse(
            request, "errors/404.html", {"user": user}, status_code=404
        )
    from fastapi.responses import JSONResponse
    detail = getattr(exc, "detail", "An error occurred")
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


# Handle both FastAPI and Starlette HTTPExceptions (route-not-found uses Starlette's)
@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return await _handle_http_exception(request, exc)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return await _handle_http_exception(request, exc)


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse(
            request, "errors/500.html", {"user": None}, status_code=500
        )
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Routers
app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(feedback.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.app_name, "version": "0.1.0"}


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_optional_user(request, db)
    return templates.TemplateResponse(request, "landing.html", {"settings": settings, "user": user})
