# Test cases for the caching module. (KAN-30)

# These tests use a fake in-memory Redis client to avoid needing a real Redis server.

import redis

from app.core import cache


class FakeRedis: # Use this class to simulate a Redis client in memory for testing purposes.
                 # It has a simple dictionary to store key-value pairs and another dictionary to store TTLs (time-to-live) for each key.
    def __init__(self):
        self.store = {}
        self.ttls = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ex=None):
        self.store[key] = value
        self.ttls[key] = ex


def test_cached_calls_fetch_once(monkeypatch): # Test that the cached function calls the fetch function only once and caches the result in Redis.
    fake = FakeRedis()
    monkeypatch.setattr(cache, "get_redis", lambda: fake)
    calls = []

    def fetch():
        calls.append(1)
        return {"personaname": "Bob"}

    first = cache.cached("steam:summary:1", 3600, fetch)
    second = cache.cached("steam:summary:1", 3600, fetch)

    assert first == {"personaname": "Bob"}
    assert second == {"personaname": "Bob"}
    assert len(calls) == 1
    assert fake.ttls["steam:summary:1"] == 3600


def test_cached_works_without_redis(monkeypatch): # Test that the cached function still works even if Redis is down or misconfigured,
                                                  # by calling the fetch function directly and returning its result without caching it.
    def broken():
        raise redis.ConnectionError("Redis is down")

    monkeypatch.setattr(cache, "get_redis", broken)

    result = cache.cached("steam:summary:1", 3600, lambda: {"personaname": "Bob"})

    assert result == {"personaname": "Bob"}
