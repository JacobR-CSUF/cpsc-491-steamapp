from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.services.steam_client import PrivateProfileError, SteamApiError
from app.controllers.health import router as health_router
from app.controllers.players import router as players_router
from app.controllers.screenshots import router as screenshots_router
from app.core.config import get_settings
from app.controllers.achievements import router as achievements_router
from app.controllers.stats import router as stats_router
from app.controllers.comparisons import router as comparisons_router
from app.controllers.game_details import router as game_details_router
from app.controllers.history import router as history_router
from app.controllers.advanced import router as advanced_router
from app.controllers.playtime import router as playtime_router


def create_app() -> FastAPI:
    app = FastAPI(title="Steam-User Showdown")
    settings = get_settings()
    @app.exception_handler(PrivateProfileError)
    async def private_profile_handler(
        request: Request, exc: PrivateProfileError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"detail": "This player’s game details are private."},
        )

    @app.exception_handler(SteamApiError)
    async def steam_api_handler(
        request: Request, exc: SteamApiError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={"detail": "Steam couldn’t be reached. Try again in a minute."},
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(players_router)
    app.include_router(screenshots_router)
    app.include_router(achievements_router) # Include the achievements router to handle achievement-related API endpoints
    app.include_router(stats_router)
    app.include_router(comparisons_router)
    app.include_router(game_details_router)
    app.include_router(history_router)
    app.include_router(advanced_router)
    app.include_router(playtime_router)

    return app

app = create_app()

