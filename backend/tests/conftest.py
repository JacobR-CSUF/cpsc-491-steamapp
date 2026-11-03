import httpx
import pytest

from app.services import steam_client


@pytest.fixture(autouse=True)
def block_external_requests(monkeypatch):
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(503)))
    monkeypatch.setattr(steam_client, "http_client", client)
