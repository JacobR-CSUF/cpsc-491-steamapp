import httpx
import pytest

from app.services import steam_client, store_prices


def use_mock_transport(monkeypatch: pytest.MonkeyPatch, handler) -> None:
    client = httpx.Client(transport=httpx.MockTransport(handler), timeout=15.0)
    monkeypatch.setattr(steam_client, "http_client", client)


def use_memory_cache(monkeypatch: pytest.MonkeyPatch) -> dict:
    store: dict = {}
    monkeypatch.setattr(store_prices, "get_json", lambda key: store.get(key))
    monkeypatch.setattr(
        store_prices, "set_json", lambda key, value, ttl_seconds: store.__setitem__(key, value)
    )
    return store


def priced(app_ids: list[str], cents: int = 1999) -> dict:
    return {
        app_id: {"success": True, "data": {"price_overview": {"currency": "USD", "initial": cents, "final": cents}}}
        for app_id in app_ids
    }


def test_fetch_prices_batches_requests(monkeypatch):
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        assert request.url.params["filters"] == "price_overview"
        assert request.url.params["cc"] == "us"
        return httpx.Response(200, json=priced(request.url.params["appids"].split(",")))

    use_mock_transport(monkeypatch, handler)

    prices = store_prices.fetch_prices(list(range(1, 121)))

    assert len(requests) == 3
    assert [len(r.url.params["appids"].split(",")) for r in requests] == [50, 50, 20]
    assert prices == {app_id: 1999 for app_id in range(1, 121)}


def test_parse_price_handles_free_and_failed():
    paid = {"success": True, "data": {"price_overview": {"initial": 5999, "final": 2999}}}

    assert store_prices.parse_price(paid) == 5999
    assert store_prices.parse_price({"success": True, "data": []}) == 0
    assert store_prices.parse_price({"success": False}) == 0
    assert store_prices.parse_price(None) == 0


def test_get_prices_uses_cache(monkeypatch):
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.params["appids"])
        return httpx.Response(200, json=priced(request.url.params["appids"].split(",")))

    use_mock_transport(monkeypatch, handler)
    store = use_memory_cache(monkeypatch)
    store[store_prices.price_key(10)] = 500

    first = store_prices.get_prices([10, 20, 30])
    second = store_prices.get_prices([10, 20, 30])

    assert first == second == {10: 500, 20: 1999, 30: 1999}
    assert calls == ["20,30"]


def test_failed_request_is_not_cached(monkeypatch):
    use_mock_transport(monkeypatch, lambda request: httpx.Response(503))
    store = use_memory_cache(monkeypatch)

    assert store_prices.get_prices([40, 50]) == {40: 0, 50: 0}
    assert store == {}


def test_get_prices_works_without_redis(monkeypatch):
    def unreachable(*args):
        raise ConnectionError("Redis is down")

    use_mock_transport(monkeypatch, lambda request: httpx.Response(200, json=priced(["60"])))
    monkeypatch.setattr(store_prices, "get_json", unreachable)
    monkeypatch.setattr(store_prices, "set_json", unreachable)

    assert store_prices.get_prices([60]) == {60: 1999}
