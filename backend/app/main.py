from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.health import router as health_router
from app.core.config import get_settings

def create_app() -> FastAPI:
    app = FastAPI(title="Steam-User Showdown")
    settings = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    return app

app = create_app()