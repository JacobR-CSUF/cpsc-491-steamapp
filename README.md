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

## Frontend
