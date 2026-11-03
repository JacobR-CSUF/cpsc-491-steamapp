import logging
from itertools import batched

import httpx

from app.core.cache import get_json, set_json
from app.services import steam_client

logger = logging.getLogger(__name__)

STORE_API_URL = "https://store.steampowered.com/api/appdetails"
BATCH_SIZE = 50
PRICE_TTL_SECONDS = 24 * 60 * 60


def price_key(app_id: int) -> str:
    return f"steam:price:{app_id}"


def parse_price(entry) -> int:
    if not isinstance(entry, dict) or not entry.get("success"):
        return 0
    data = entry.get("data")
    if not isinstance(data, dict):
        return 0
    price = data.get("price_overview") or {}
    return int(price.get("initial") or 0)


def fetch_prices(app_ids: list[int]) -> dict[int, int]:
    prices: dict[int, int] = {}
    for batch in batched(app_ids, BATCH_SIZE):
        params = {
            "appids": ",".join(str(app_id) for app_id in batch),
            "filters": "price_overview",
            "cc": "us",
        }
        try:
            response = steam_client.http_client.get(STORE_API_URL, params=params)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Store price request failed for %d apps: %s", len(batch), exc)
            continue
        if not isinstance(payload, dict):
            logger.warning("Store price request returned no data for %d apps", len(batch))
            continue
        for app_id in batch:
            prices[app_id] = parse_price(payload.get(str(app_id)))
    return prices


def get_prices(app_ids) -> dict[int, int]:
    unique_ids = list(dict.fromkeys(int(app_id) for app_id in app_ids))
    prices: dict[int, int] = {}
    missing: list[int] = []

    for app_id in unique_ids:
        try:
            cached_price = get_json(price_key(app_id))
        except Exception as exc:
            logger.warning("Cache read failed for %s: %s", price_key(app_id), exc)
            cached_price = None
        if cached_price is None:
            missing.append(app_id)
        else:
            prices[app_id] = cached_price

    fetched = fetch_prices(missing)
    for app_id, cents in fetched.items():
        try:
            set_json(price_key(app_id), cents, PRICE_TTL_SECONDS)
        except Exception as exc:
            logger.warning("Cache write failed for %s: %s", price_key(app_id), exc)
    prices.update(fetched)

    for app_id in missing:
        prices.setdefault(app_id, 0)
    return prices
