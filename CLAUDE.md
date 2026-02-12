# FeedbackCue

Phase: DEVELOPMENT

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
- **Auth**: JWT access tokens stored in httponly cookies, bcrypt password hashing via passlib
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
- [ ] Write README with setup and deploy instructions

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

## Known Issues
- Starlette DeprecationWarning on TemplateResponse signature (cosmetic, non-breaking)

## Files Structure
```
feedback-cue/
├── CLAUDE.md
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
