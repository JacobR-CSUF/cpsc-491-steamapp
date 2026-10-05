from fastapi import APIRouter
from app.services.health import check_postgres, check_redis

router = APIRouter(prefix="/api")

@router.get("/health")
def health():
    return {
        "api": "ok",
        "postgres": check_postgres(),
        "redis": check_redis()
    }