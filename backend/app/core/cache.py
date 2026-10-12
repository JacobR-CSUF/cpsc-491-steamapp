# Redis cache helpers (KAN-30).

# If Redis is down or misconfigured, every helper degrades gracefully so the
# app keeps working by calling the Steam API directly.

import json
import logging
import os
from functools import lru_cache

import redis

logger = logging.getLogger(__name__)

DEFAULT_REDIS_URL = "redis://localhost:6379/0"


@lru_cache(maxsize=1)
def get_redis():
    """Return a cached Redis client for REDIS_URL."""
    url = os.environ.get("REDIS_URL", DEFAULT_REDIS_URL) # This is set in docker-compose.yml and in Heroku config vars.
    return redis.Redis.from_url(
        url,
        decode_responses=True, # decode bytes to str for JSON
        socket_connect_timeout=1,  # fail fast when Redis is unreachable
        socket_timeout=1,
    )


def get_json(key):
    """Return the decoded JSON value stored at key, or None if missing."""
    raw = get_redis().get(key) # grabs the value from Redis, which is a string (or None if the key doesn't exist)
    if raw is None: # if the key doesn't exist in Redis, return None
        return None
    return json.loads(raw)


def set_json(key, value, ttl_seconds):
    """Store a JSON-serializable value at key, expiring after ttl_seconds."""
    get_redis().set(key, json.dumps(value), ex=ttl_seconds) # store the value in Redis as a JSON string, with an expiration time


def cached(key, ttl_seconds, fetch):
    """Return the cached value for key, or call fetch() and cache the result.

    If Redis is unreachable, fetch() is called directly and nothing is cached.
    A fetch() result of None is returned but not cached, because None is how
    get_json() reports a miss.
    """
    try:
        hit = get_json(key)
    except Exception as exc:  # Redis down, bad JSON, etc.
        logger.warning("Cache read failed for %s: %s", key, exc)
        return fetch()

    if hit is not None: # if the value is found in the cache, return it
        return hit

    value = fetch()
    if value is not None: # if the value is not None, cache it
        try:
            set_json(key, value, ttl_seconds) # store the value in Redis with the specified TTL
        except Exception as exc:
            logger.warning("Cache write failed for %s: %s", key, exc) # log a warning if the cache write fails, but still return the value
    return value
