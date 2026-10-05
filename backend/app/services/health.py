import psycopg
import redis
from app.core.config import get_settings

def check_postgres():
    settings = get_settings()
    try:
        with psycopg.connect(settings.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                return "ok" if cur.fetchone() else "error"
    except Exception:
        return "error"

def check_redis():
    settings = get_settings()
    try:
        r = redis.Redis.from_url(settings.redis_url)
        return "ok" if r.ping() else "error"
    except Exception:
        return "error"