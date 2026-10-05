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

## Frontend
Requires Node.js 24.

From the repository root, install dependencies:

```console
cd frontend
npm install
```

Create the frontend's local environment file:

```console
# macOS/Linux
cp .env.example .env.local

# Windows PowerShell
Copy-Item .env.example .env.local
```

The default backend URL in `.env.local` is:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend:

```console
npm run dev
```

Open http://localhost:3000.

The home page displays backend service statuses and refreshes every
10 seconds. If the backend cannot be reached, it displays
"Backend unreachable".

Run lint checks from the frontend directory:

```console
npm run lint
```

On Windows PowerShell, use `npm.cmd` instead of `npm` if script
execution is blocked.
