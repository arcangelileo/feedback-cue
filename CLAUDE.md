# FeedbackCue

Phase: DEPLOYMENT

## Project Spec
- **Repo**: https://github.com/arcangelileo/feedback-cue
- **Idea**: FeedbackCue is a customer feedback and feature request board for SaaS companies, product teams, and indie developers. Users create a branded feedback portal where their customers can submit feature requests, report bugs, and vote on ideas. The product owner can organize feedback into categories, update statuses (planned, in progress, shipped), and see what matters most — all without spreadsheets or cluttered email threads. Think a streamlined, self-hostable alternative to Canny or UserVoice.
- **Target users**: SaaS founders, product managers, indie hackers, and small development teams who need to collect and prioritize customer feedback without enterprise pricing. Secondary: agencies managing feedback for multiple client projects.
- **Revenue model**: Freemium SaaS. Free tier: 1 board, 50 feedback items. Paid tier ($12/mo): unlimited boards, unlimited items, custom branding, CSV export, email notifications. Future: team seats, API access, webhooks, integrations.
- **Tech stack**: Python, FastAPI, SQLite (MVP via async SQLAlchemy + aiosqlite), Jinja2 + Tailwind CSS (CDN), APScheduler for background jobs, Docker for deployment.
- **MVP scope**:
  1. User registration & login (JWT httponly cookies)
  2. Create/manage feedback boards (each board has a unique public slug)
  3. Public-facing board page where anyone can submit feedback and vote
  4. Board owner dashboard: view all feedback, filter by status/category/votes, update status
  5. Voter identification (optional email or anonymous)
  6. Status labels: Open, Under Review, Planned, In Progress, Shipped, Closed
  7. Category tagging (Bug, Feature, Improvement, Question)
  8. Sort by: most votes, newest, trending
  9. Admin board settings (title, description, accent color)
  10. Responsive, professional UI with Tailwind CSS

## Architecture Decisions
- **src layout**: `src/app/` with `api/`, `models/`, `schemas/`, `services/`, `templates/` subdirectories
- **Auth**: JWT access tokens stored in httponly cookies, bcrypt password hashing
- **Database**: Async SQLAlchemy 2.0 + aiosqlite for SQLite; Alembic for migrations from day one
- **Background jobs**: APScheduler integrated into FastAPI lifespan (for future email digests, vote tallies)
- **Templates**: Jinja2 with Tailwind CSS via CDN, Inter font, consistent color palette (indigo primary)
- **Configuration**: Pydantic Settings loading from .env
- **Public boards**: No auth required to view/vote; optional email capture for voters
- **Board slugs**: Unique, URL-safe slugs auto-generated from board name, editable by owner
- **Voting**: One vote per item per voter (tracked by session cookie for anonymous, by email if provided)
- **Testing**: pytest + httpx async test client, in-memory SQLite for tests
- **Docker**: Multi-stage build, non-root user, docker-compose with volume for SQLite persistence

## Task Backlog
- [x] Create GitHub repo and initial project structure (pyproject.toml, src layout, .env.example)
- [x] Set up FastAPI app skeleton with health check, config, and database engine
- [x] Create SQLAlchemy models: User, Board, FeedbackItem, Vote
- [x] Set up Alembic and generate initial migration
- [x] Implement user registration and login API + pages (JWT auth)
- [x] Implement board CRUD — create, update, delete boards with unique slugs
- [x] Build owner dashboard page — list boards, view feedback per board, filter/sort
- [x] Build public board page — view feedback, submit new items, vote on items
- [x] Implement voting system with duplicate-vote prevention
- [x] Implement feedback status management (owner can update status labels)
- [x] Add category tagging and filtering
- [x] Build board settings page (title, description, accent color)
- [x] Add landing/marketing page and navigation
- [x] Write comprehensive tests (auth, boards, feedback, voting)
- [x] Write Dockerfile and docker-compose.yml
- [x] Write README with setup and deploy instructions
- [x] QA pass: bug fixes, UI polish, error pages, test coverage

## Progress Log
### Session 1 — IDEATION
- Chose idea: FeedbackCue — customer feedback & feature request boards
- Created spec and backlog
- Rationale: Strong B2B demand (every SaaS needs feedback collection), clear freemium model, sticky product, well-scoped MVP, differentiated from existing factory projects (InvoicePulse=billing, StatusPing=monitoring)

### Session 2 — SCAFFOLDING
- Created full project structure with all files from the architecture spec
- **FastAPI app**: main.py with lifespan, health check endpoint, landing page route
- **Config**: Pydantic Settings with .env support (database URL, JWT config, server settings)
- **Database**: Async SQLAlchemy 2.0 engine + session factory, DeclarativeBase
- **Models**: User, Board, FeedbackItem (with status/category enums), Vote (with unique constraint)
- **Services**: Auth (JWT+bcrypt, register/login/token), Board (CRUD, unique slug generation), Feedback (CRUD, vote toggle with dedup)
- **API routes**: Auth (form + JSON endpoints), Boards (dashboard CRUD, status updates), Feedback (public board, submit, vote)
- **Templates**: 8 Jinja2 templates with Tailwind CSS — landing page with hero/features/pricing, auth forms, dashboard (board list, detail with filters, settings), public board page with voting UI
- **Alembic**: Configured for async SQLite migrations
- **Docker**: Multi-stage Dockerfile (non-root user), docker-compose with volume
- **Tests**: 27 tests all passing — auth (12), boards (8), feedback (4), voting (3)
- Created GitHub repo at https://github.com/arcangelileo/feedback-cue

### Session 3 — QA & DOCUMENTATION
- **Quality audit**: Reviewed entire codebase (all source files, templates, tests, config)
- **Fixed Starlette DeprecationWarning**: Updated all TemplateResponse calls across auth.py, boards.py, feedback.py, main.py to use new signature `TemplateResponse(request, name, context)` — all 10 deprecation warnings eliminated
- **Generated initial Alembic migration**: `alembic revision --autogenerate` created migration with all 4 tables (users, boards, feedback_items, votes) with proper indexes and constraints
- **Fixed footer year**: Updated landing page copyright from 2025 to 2026
- **Removed unused import**: Cleaned up `StaticFiles` import from main.py
- **Wrote comprehensive README.md**: Quick start guide, Docker deployment instructions, environment variables reference, project structure, API endpoints, and usage guide
- **All 27 tests passing** with zero warnings
- **All backlog items complete** — Phase changed to QA

### Session 4 — QA POLISH & BUG FIXES
- **Full codebase review**: Read all 20+ source files, all 10 templates, all test files
- **Bugs found and fixed:**
  1. **Unused `EmailStr` import** in `schemas/auth.py` — removed dead import
  2. **Voter cookie bug**: `get_voter_id()` in deps.py set cookie on a `Response` object that was never sent back (the actual response was a `TemplateResponse`). Refactored voter ID management into `feedback.py` with `_get_or_create_voter_id()` that sets the cookie directly on the actual response object (TemplateResponse or RedirectResponse)
  3. **Unused imports** in `api/deps.py`: Removed `uuid`, `Cookie`, `Response` imports and the now-unused `get_voter_id` function
  4. **404 handler missed route-not-found**: Only handled `fastapi.HTTPException` but Starlette raises `starlette.exceptions.HTTPException` for unknown routes. Added dual handler for both exception types via shared `_handle_http_exception()` helper
  5. **404 page showed no user nav**: Error handler hardcoded `user=None`. Updated to fetch actual user from session for proper nav display
  6. **Board slug update bug**: `update_board` used `del kwargs["slug"]` before popping, missing the `elif` case for empty slug. Refactored to use `kwargs.pop()` properly
- **Missing features added:**
  1. **500 error page**: Created `errors/500.html` with professional styling and "Try Again" button
  2. **500 exception handler**: Added server error handler in main.py
  3. **Feedback submission success banner**: Added `?submitted=true` query param flow with green "Thanks for your feedback!" toast on public board
  4. **Collapsible feedback form**: Form now starts collapsed when board has existing items (less noise), expanded when empty (encourage first submission)
  5. **Favicon**: Added inline SVG favicon (indigo "F" on rounded square) to base.html
  6. **Username display**: Nav bar shows username when logged in; dashboard greeting includes username; mobile menu shows "Signed in as [username]"
  7. **Copy link button**: Added "Copy link" button next to public board URL in board detail header
- **UI polish:**
  - Consistent nav across all pages with proper user state
  - Mobile menu shows signed-in user info
  - Board detail header has copy-link functionality
- **Test coverage expanded**: 48 → 63 tests (+15 new tests)
  - `test_404_returns_json_for_api`: Verifies JSON 404 for API clients
  - `test_404_returns_html_for_browser`: Verifies HTML 404 page for browsers
  - `test_401_redirects_to_login_for_browser`: Verifies auth redirect for HTML
  - `test_form_register_short_password`: Password validation on form register
  - `test_form_register_duplicate_email`: Duplicate email validation on form
  - `test_landing_page_shows_login_for_anonymous`: Landing page state for anon
  - `test_landing_page_shows_dashboard_for_logged_in`: Landing page state for auth user
  - `test_create_board_form_success`: Board creation via HTML form
  - `test_board_slug_update_persists`: Slug update works end-to-end
  - `test_dashboard_shows_username`: Username visible on dashboard
  - `test_board_detail_empty_state`: Empty state shows slug and message
  - `test_delete_nonexistent_board`: 404 for deleting missing board
  - `test_submit_feedback_shows_success_banner`: Success toast after submission
  - `test_public_board_sets_voter_cookie`: Voter cookie set on first visit
  - `test_public_board_form_collapsed_with_items`: Form collapsed when items exist
- **All 63 tests passing** — Phase changed to DEPLOYMENT

## Known Issues
- None currently

## Files Structure
```
feedback-cue/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── docker-entrypoint.sh
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── c8201dc28b46_initial_migration.py
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── boards.py
│       │   ├── deps.py
│       │   └── feedback.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── board.py
│       │   ├── feedback.py
│       │   └── vote.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── board.py
│       │   └── feedback.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── board.py
│       │   └── feedback.py
│       └── templates/
│           ├── base.html
│           ├── landing.html
│           ├── auth/
│           │   ├── login.html
│           │   └── register.html
│           ├── dashboard/
│           │   ├── boards.html
│           │   ├── board_detail.html
│           │   └── board_settings.html
│           ├── errors/
│           │   ├── 404.html
│           │   └── 500.html
│           └── public/
│               └── board.html
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_auth.py
    ├── test_boards.py
    ├── test_feedback.py
    └── test_voting.py
```
