# Steam-User Showdown

Compares two public Steam profiles by achievements, completed games, and library stats.

## Tech Stack

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: FastAPI, Python
- Database: PostgreSQL
- Cache: Redis
- Containers: Docker Compose

## Prerequisites

- Git
- Docker Desktop
- Node.js 24
- Python 3.12
- VS Code

## Branch and Commit Format

- Branch: `KAN-<number>-short-description`
- Commit: `KAN-<number> - message`

## Environment Variables

Create your local environment file from the shared template in the repository root:

```console
# macOS/Linux
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

Open `.env` and paste your Steam Web API key after `STEAM_API_KEY=`. Never commit `.env`; it is ignored by Git. Confirm that with:

```console
git check-ignore .env
```

Verify Steam Web API access with a public SteamID64:

```console
python3 scripts/check_steam_api.py <steamid64>
```

On Windows, if `python3` is not available, use:

```console
python scripts/check_steam_api.py <steamid64>
```

Your SteamID64 is available from your Steam account details page. The script prints the display name, profile visibility, and owned-game count; if the game library is private, it reports it as hidden.

## Database and Cache
On Windows, install WSL 2 **before** Docker Desktop. Confirm Docker works with `docker run hello-world`.

```console
docker compose up -d     # start Postgres and Redis
docker compose ps        # check both are healthy
docker compose down      # stop them
docker compose down -v   # wipe all data
```

Quick tests:
```console
docker compose exec postgres psql -U showdown -d showdown -c "SELECT 1;"
docker compose exec redis redis-cli ping   # prints PONG
```

Credentials and ports are read from .env. If port 5432 or 6379 is taken, change POSTGRES_PORT or REDIS_PORT there.

## Backend

The backend is built with FastAPI and runs on Python 3.12. All commands below should be executed from inside the `backend/` directory.

### Environment Setup

Create and activate a Python virtual environment:

**Windows (Command Prompt):**
```console
cd backend
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```console
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```console
pip install -r requirements.txt
```

### Run the Server

Start Postgres and Redis from the repository root with `docker compose up -d`, then run from `backend/`:

```console
fastapi dev app/main.py
```

The API is available at `http://localhost:8000`. Check service status at
`http://localhost:8000/api/health` and interactive API docs at
`http://localhost:8000/docs`.

### Run Tests

Run the test suite from `backend/`:

```console
python -m pytest
```

## Frontend
