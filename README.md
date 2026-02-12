# FeedbackCue

**Customer feedback and feature request boards for SaaS companies.**

FeedbackCue lets you create branded feedback portals where your customers can submit feature requests, report bugs, and vote on ideas. Prioritize what matters most — without spreadsheets or cluttered email threads.

## Features

- **Public feedback boards** — Share a link; users submit ideas and vote without creating an account
- **Voting & prioritization** — Users upvote features they want; you see demand at a glance
- **Status tracking** — Mark items as Open, Under Review, Planned, In Progress, Shipped, or Closed
- **Category tagging** — Organize feedback as Bug, Feature, Improvement, or Question
- **Custom branding** — Set accent colors and descriptions per board
- **Owner dashboard** — Filter by status/category, sort by votes/date, manage feedback
- **Anonymous or identified** — Optional email capture for follow-ups, zero-friction voting
- **Unique board slugs** — Each board gets a clean public URL (`/b/your-product`)

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), aiosqlite
- **Frontend:** Jinja2 templates, Tailwind CSS (CDN), Inter font
- **Auth:** JWT access tokens in httponly cookies, bcrypt password hashing
- **Database:** SQLite (async via aiosqlite), Alembic migrations
- **Deployment:** Docker, docker-compose

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip

### 1. Clone the repository

```bash
git clone https://github.com/arcangelileo/feedback-cue.git
cd feedback-cue
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set a secure `SECRET_KEY`:

```
SECRET_KEY=your-random-secret-key-here
```

### 5. Initialize the database

The app auto-creates tables on startup for development. For production, use Alembic:

```bash
alembic upgrade head
```

### 6. Run the development server

```bash
uvicorn app.main:app --reload --app-dir src
```

Visit [http://localhost:8000](http://localhost:8000) to see the app.

## Usage

1. **Register** an account at `/register`
2. **Create a board** from the dashboard — give it a name, description, and accent color
3. **Share the public link** (`/b/your-board-slug`) with your users
4. Users **submit feedback** and **vote** on existing items — no account required
5. **Manage feedback** from your dashboard — filter, sort, and update statuses

## Running Tests

```bash
pytest tests/ -v
```

Tests use an in-memory SQLite database and cover:

- Authentication (registration, login, logout, JWT tokens)
- Board CRUD (create, list, detail, settings, delete)
- Feedback submission (with author info and anonymous)
- Voting (toggle, duplicate prevention)

## Docker Deployment

### Using docker-compose (recommended)

```bash
# Set your secret key
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Build and start
docker-compose up -d
```

The app will be available at [http://localhost:8000](http://localhost:8000).

### Using Docker directly

```bash
# Build the image
docker build -t feedbackcue .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e ENVIRONMENT=production \
  -v feedbackcue-data:/app/data \
  feedbackcue
```

### Production considerations

- **Set `SECRET_KEY`** to a strong random value (never use the default)
- **Set `ENVIRONMENT=production`** to disable SQL echo logging
- **Use a reverse proxy** (nginx, Caddy) for TLS termination
- **Back up the SQLite database** file at `data/feedbackcue.db`
- The Docker image runs as a non-root user for security

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `FeedbackCue` | Application name shown in UI |
| `SECRET_KEY` | `change-me-...` | JWT signing key (change in production!) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/feedbackcue.db` | Database connection string |
| `ENVIRONMENT` | `development` | Set to `production` to disable debug logging |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_EXPIRE_MINUTES` | `1440` | Token expiry (default: 24 hours) |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server bind port |

## Project Structure

```
feedback-cue/
├── src/app/              # Application source code
│   ├── main.py           # FastAPI app, lifespan, routes
│   ├── config.py         # Pydantic settings
│   ├── database.py       # Async SQLAlchemy engine
│   ├── api/              # Route handlers
│   │   ├── auth.py       # Registration, login, logout
│   │   ├── boards.py     # Dashboard, board CRUD, status updates
│   │   ├── feedback.py   # Public board, submit, vote
│   │   └── deps.py       # Auth dependencies, voter ID
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Business logic layer
│   └── templates/        # Jinja2 HTML templates
├── tests/                # pytest test suite
├── alembic/              # Database migrations
├── Dockerfile            # Multi-stage Docker build
├── docker-compose.yml    # Docker Compose config
└── pyproject.toml        # Python project config
```

## API Endpoints

### Pages (HTML)

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Landing page |
| `GET` | `/register` | Registration form |
| `POST` | `/register` | Process registration |
| `GET` | `/login` | Login form |
| `POST` | `/login` | Process login |
| `GET` | `/logout` | Log out |
| `GET` | `/dashboard` | Board list (auth required) |
| `GET` | `/dashboard/boards/:id` | Board detail with feedback |
| `GET` | `/dashboard/boards/:id/settings` | Board settings |
| `GET` | `/b/:slug` | Public board page |

### JSON API

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register user |
| `POST` | `/api/auth/login` | Login user |
| `POST` | `/api/boards` | Create board |
| `GET` | `/api/boards` | List boards |
| `GET` | `/health` | Health check |

## License

MIT
