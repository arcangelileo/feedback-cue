# FeedbackCue

**Customer feedback and feature request boards for SaaS companies.**

FeedbackCue lets you create branded feedback portals where your customers can submit feature requests, report bugs, and vote on ideas. Prioritize what matters most — without spreadsheets or cluttered email threads.

A streamlined, self-hostable alternative to Canny or UserVoice.

---

## Features

- **Public feedback boards** — Share a link; users submit ideas and vote without creating an account
- **Voting & prioritization** — Users upvote features they want; you see demand at a glance
- **Status tracking** — Mark items as Open, Under Review, Planned, In Progress, Shipped, or Closed
- **Category tagging** — Organize feedback as Bug, Feature, Improvement, or Question
- **Custom branding** — Set accent colors and descriptions per board
- **Owner dashboard** — Filter by status/category, sort by votes/date, manage all feedback
- **Anonymous or identified** — Optional email capture for follow-ups, zero-friction anonymous voting
- **Unique board slugs** — Each board gets a clean public URL (`/b/your-product`)
- **Responsive design** — Works on desktop, tablet, and mobile
- **One-click deploy** — Docker image with health checks and auto-migrations

---

## Quick Start

### Docker (recommended)

```bash
# Generate a secret key
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Start FeedbackCue
docker compose up -d

# Open http://localhost:8000
```

That's it. The app runs migrations automatically and persists data in a Docker volume.

### Local Development

```bash
# Clone
git clone https://github.com/arcangelileo/feedback-cue.git
cd feedback-cue

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Configure
cp .env.example .env

# Run
uvicorn app.main:app --reload --app-dir src
```

Visit [http://localhost:8000](http://localhost:8000). The database is created automatically on first run.

---

## Usage

1. **Register** an account at `/register`
2. **Create a board** from the dashboard — give it a name, description, and accent color
3. **Share the public link** (`/b/your-board-slug`) with your users
4. Users **submit feedback** and **vote** on existing items — no account required
5. **Manage feedback** from your dashboard — filter, sort, update statuses, and track votes

---

## Tech Stack

| Component | Technology |
|---|---|
| **Backend** | Python 3.11+, FastAPI |
| **Database** | SQLite (async via SQLAlchemy 2.0 + aiosqlite) |
| **Migrations** | Alembic |
| **Auth** | JWT access tokens in httpOnly cookies, bcrypt |
| **Frontend** | Jinja2 templates, Tailwind CSS (CDN), Inter font |
| **Deployment** | Docker with multi-stage build |

---

## Docker Deployment

### Using docker compose (recommended)

```bash
# Set your secret key (required for production)
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Build and start
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f app

# Stop
docker compose down
```

### Using Docker directly

```bash
# Build the image
docker build -t feedbackcue .

# Run the container
docker run -d \
  --name feedbackcue \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key-here \
  -e ENVIRONMENT=production \
  -v feedbackcue-data:/app/data \
  --restart unless-stopped \
  feedbackcue
```

### Production Checklist

- [ ] Set `SECRET_KEY` to a strong random value (never use the default)
- [ ] Set `ENVIRONMENT=production` to disable SQL debug logging
- [ ] Use a reverse proxy (nginx, Caddy, Traefik) for TLS termination
- [ ] Back up the SQLite database file regularly (`/app/data/feedbackcue.db` inside the container, or the `app-data` volume)
- [ ] The Docker image runs as a non-root user (`appuser`) for security
- [ ] Health check is built into the image at `/health`

### Backing Up the Database

```bash
# Copy from Docker volume
docker cp feedbackcue:/app/data/feedbackcue.db ./backup-$(date +%Y%m%d).db

# Or with docker compose
docker compose exec app cp /app/data/feedbackcue.db /app/data/backup.db
docker compose cp app:/app/data/backup.db ./backup-$(date +%Y%m%d).db
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `FeedbackCue` | Application name shown in the UI |
| `SECRET_KEY` | `change-me-...` | JWT signing key (**must change in production**) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/feedbackcue.db` | Database connection string |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_EXPIRE_MINUTES` | `1440` | Token expiry in minutes (default: 24 hours) |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server bind port |

See `.env.example` for a fully commented configuration template.

---

## API Reference

### Pages (HTML)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/` | No | Landing page |
| `GET` | `/register` | No | Registration form |
| `POST` | `/register` | No | Process registration |
| `GET` | `/login` | No | Login form |
| `POST` | `/login` | No | Process login |
| `GET` | `/logout` | No | Log out (clears cookie) |
| `GET` | `/dashboard` | Yes | Board list |
| `POST` | `/dashboard/boards` | Yes | Create board (form) |
| `GET` | `/dashboard/boards/:id` | Yes | Board detail with feedback |
| `GET` | `/dashboard/boards/:id/settings` | Yes | Board settings page |
| `POST` | `/dashboard/boards/:id/settings` | Yes | Update board settings |
| `POST` | `/dashboard/boards/:id/delete` | Yes | Delete a board |
| `POST` | `/dashboard/boards/:id/feedback/:item_id/status` | Yes | Update feedback status |
| `GET` | `/b/:slug` | No | Public board page |
| `POST` | `/b/:slug/submit` | No | Submit feedback (form) |
| `POST` | `/b/:slug/vote/:item_id` | No | Vote/unvote on feedback |

### JSON API

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | No | Register a new user |
| `POST` | `/api/auth/login` | No | Authenticate and get token |
| `POST` | `/api/boards` | Yes | Create a new board |
| `GET` | `/api/boards` | Yes | List your boards |
| `GET` | `/health` | No | Health check |

#### Register (JSON)

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "username": "yourname", "password": "securepass123"}'
```

Response:
```json
{
  "user": {"id": "uuid", "email": "you@example.com", "username": "yourname"},
  "token": "eyJ..."
}
```

#### Login (JSON)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "securepass123"}'
```

#### Create Board (JSON)

```bash
curl -X POST http://localhost:8000/api/boards \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=YOUR_TOKEN" \
  -d '{"name": "My Product", "description": "Feedback for My Product", "accent_color": "#4F46E5"}'
```

Response:
```json
{
  "id": "uuid",
  "name": "My Product",
  "slug": "my-product",
  "description": "Feedback for My Product",
  "accent_color": "#4F46E5",
  "owner_id": "uuid",
  "created_at": "2026-02-13T...",
  "updated_at": "2026-02-13T..."
}
```

#### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "healthy", "app": "FeedbackCue", "version": "0.1.0"}
```

---

## Architecture

```
src/app/
├── main.py              # FastAPI application, lifespan, exception handlers, routes
├── config.py            # Pydantic Settings (loads from .env)
├── database.py          # Async SQLAlchemy engine & session factory
├── api/                 # Route handlers (controllers)
│   ├── auth.py          # Registration, login, logout (HTML + JSON)
│   ├── boards.py        # Dashboard CRUD, board settings, status updates
│   ├── feedback.py      # Public board, feedback submission, voting
│   └── deps.py          # Shared dependencies (auth, voter ID)
├── models/              # SQLAlchemy ORM models
│   ├── user.py          # User (email, username, hashed_password)
│   ├── board.py         # Board (name, slug, description, accent_color, owner)
│   ├── feedback.py      # FeedbackItem (title, status, category, vote_count)
│   └── vote.py          # Vote (unique per voter per item)
├── schemas/             # Pydantic request/response schemas
│   ├── auth.py          # UserRegister, UserLogin, UserResponse
│   ├── board.py         # BoardCreate, BoardUpdate, BoardResponse
│   └── feedback.py      # FeedbackCreate, FeedbackResponse, VoteRequest
├── services/            # Business logic layer
│   ├── auth.py          # Password hashing, JWT, user queries
│   ├── board.py         # Board CRUD, slug generation, stats
│   └── feedback.py      # Feedback CRUD, vote toggle, dedup
└── templates/           # Jinja2 HTML templates with Tailwind CSS
    ├── base.html        # Shared layout, nav, footer
    ├── landing.html     # Marketing landing page
    ├── auth/            # Login & register forms
    ├── dashboard/       # Board list, detail, settings
    ├── errors/          # 404 & 500 error pages
    └── public/          # Public board with voting
```

### Key Design Decisions

- **Async everything**: All database operations use async SQLAlchemy 2.0 with `aiosqlite` for non-blocking I/O
- **JWT in httpOnly cookies**: Secure by default — tokens can't be accessed by JavaScript
- **Public boards without auth**: Anyone can view, submit, and vote — zero friction for end users
- **Voter deduplication**: Anonymous voters get a session cookie; named voters tracked by email
- **Service layer**: Business logic separated from route handlers for testability
- **Alembic from day one**: Schema changes tracked in migration files, not auto-created

---

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run with coverage
coverage run -m pytest tests/ -v
coverage report -m
```

The test suite includes **63 tests** covering:

- **Authentication**: Registration, login, logout, JWT tokens, form validation, duplicate detection
- **Boards**: CRUD operations, slug generation, settings, filtering, stats
- **Feedback**: Submission, anonymous posting, category filtering, success banners
- **Voting**: Toggle votes, duplicate prevention, HTTP endpoint voting
- **Error handling**: 404 pages (HTML + JSON), 401 redirects, form validation errors

Tests use an **in-memory SQLite database** and run in isolation (tables created/dropped per test).

---

## Database Migrations

FeedbackCue uses Alembic for database schema management.

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe your changes"

# View migration history
alembic history

# Downgrade one step
alembic downgrade -1
```

In Docker, migrations run automatically on container start via the entrypoint script.

---

## Project Structure

```
feedback-cue/
├── CLAUDE.md               # Project spec and progress log
├── README.md               # This file
├── pyproject.toml           # Python project config & dependencies
├── .env.example             # Environment variable template
├── .gitignore
├── .dockerignore
├── Dockerfile               # Multi-stage production Docker build
├── docker-compose.yml       # Docker Compose config
├── docker-entrypoint.sh     # Container entrypoint (migrations + start)
├── alembic.ini              # Alembic configuration
├── alembic/
│   ├── env.py               # Async migration environment
│   ├── script.py.mako       # Migration template
│   └── versions/            # Migration files
├── src/
│   └── app/                 # Application source code
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── api/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       └── templates/
└── tests/
    ├── conftest.py           # Test fixtures & database setup
    ├── test_auth.py
    ├── test_boards.py
    ├── test_feedback.py
    └── test_voting.py
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Make your changes
5. Run tests: `pytest tests/ -v`
6. Commit and push: `git push origin feature/your-feature`
7. Open a Pull Request

### Code Style

- Python code follows standard formatting conventions
- Templates use Tailwind CSS utility classes
- Business logic lives in `services/`, route handlers in `api/`
- All database operations are async

---

## License

MIT
