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
- VS Code

On Windows, install [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install) before Docker Desktop.

On Linux, Docker Engine with the Compose plugin also works. Add yourself to the `docker` group so commands run without `sudo`, then log out and back in:

```console
sudo usermod -aG docker $USER
```

Confirm Docker works:

```console
docker run hello-world
```

## Branch and Commit Format

- Branch: `KAN-<number>-short-description`
- Commit: `KAN-<number> - message`

## Environment Variables

Create `.env` in the repository root from the template.

**macOS/Linux**

```console
cp .env.example .env
```

**Windows PowerShell**

```console
Copy-Item .env.example .env
```

Paste your Steam Web API key after `STEAM_API_KEY=`. Git ignores `.env`. After editing it, run `docker compose up -d` to apply the change.

## Running the Stack

Start or update everything from the repository root:

```console
docker compose up -d --build
```

Open http://localhost:3000. The home page shows API, Postgres, and Redis status. Ports 3000 and 8000 must be free.

Edits in `backend/app` and `frontend/src` reload automatically. After changing `requirements.txt`, `package.json`, or a config file, run the command above again.

| Command | Purpose |
| --- | --- |
| `docker compose ps` | List running services |
| `docker compose logs -f backend` | Follow backend logs |
| `docker compose down` | Stop everything |
| `docker compose down -v` | Stop everything and wipe all data |

## Database and Cache

Postgres and Redis run only inside Docker. Test both:

```console
docker compose exec postgres psql -U showdown -d showdown -c "SELECT 1;"
docker compose exec redis redis-cli ping
```

The Redis test prints `PONG`.

## Backend

The API runs at http://localhost:8000. Service status is at http://localhost:8000/api/health and interactive docs are at http://localhost:8000/docs.

Run the tests:

```console
docker compose exec backend python -m pytest
```

Database migrations run when the backend starts. After changing a model in `backend/app/models`, create a migration and apply it:

```console
docker compose exec backend alembic revision --autogenerate -m "describe the change"
docker compose exec backend alembic upgrade head
```

Review the new file in `backend/alembic/versions` before committing it.

Check Steam Web API access with a public SteamID64:

```console
docker compose exec backend python scripts/check_steam_api.py <steamid64>
```

Your SteamID64 is on your Steam account details page. The script prints the display name, profile visibility, and owned-game count, or reports the library as hidden if it is private.

## Frontend

The app runs at http://localhost:3000.

Run lint checks:

```console
docker compose exec frontend npm run lint
```
