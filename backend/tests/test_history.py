from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, or_, select

from app.db.session import SessionLocal
from app.main import app
from app.models import Comparison, Player
from app.services import achievement_service, comparison_service, history_service, profile_status
from app.services.profile_status import ProfileStatus
from app.services.steam_client import PrivateProfileError, SteamApiError

PLAYER_A = "76561199999999993"
PLAYER_B = "76561199999999992"
PLAYER_C = "76561199999999991"
PLAYER_IDS = [int(PLAYER_A), int(PLAYER_B), int(PLAYER_C)]


def comparisons_query():
    return select(Comparison).where(or_(
        Comparison.player_a_id.in_(PLAYER_IDS),
        Comparison.player_b_id.in_(PLAYER_IDS),
    ))


@pytest.fixture(autouse=True)
def remove_test_rows():
    with SessionLocal() as db:
        assert not db.scalars(select(Player).where(Player.steam_id.in_(PLAYER_IDS))).all(), (
            "Test players already exist"
        )
        db.add_all([
            Player(steam_id=int(PLAYER_A), persona_name="History Player A", visibility=3),
            Player(steam_id=int(PLAYER_B), persona_name="History Player B", visibility=3),
            Player(steam_id=int(PLAYER_C), persona_name="History Player C", visibility=3),
        ])
        db.commit()
    try:
        yield
    finally:
        with SessionLocal() as db:
            # Both foreign keys cascade, removing only these players' history.
            db.execute(delete(Player).where(Player.steam_id.in_(PLAYER_IDS)))
            db.commit()
            assert not db.scalars(comparisons_query()).all()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(profile_status, "get_profile_status", lambda _: ProfileStatus.public)
    monkeypatch.setattr(achievement_service, "sync_player_data",
                        lambda db, steam_id: db.get(Player, int(steam_id)))
    with TestClient(app) as test_client:
        yield test_client


def test_record_comparison_saves_row():
    before = datetime.now(timezone.utc)
    with SessionLocal() as db:
        comparison = history_service.record_comparison(db, PLAYER_A, PLAYER_B)
        comparison_id = comparison.id
        assert comparison_id is not None
        assert comparison.compared_at.utcoffset() is not None
        assert before <= comparison.compared_at <= datetime.now(timezone.utc)

    # A fresh session verifies the insert was committed.
    with SessionLocal() as db:
        saved = db.get(Comparison, comparison_id)
        assert saved.player_a_id == int(PLAYER_A)
        assert saved.player_b_id == int(PLAYER_B)
        assert saved.compared_at == comparison.compared_at


def test_successful_comparisons_saved_each_time(client):
    for player_a, player_b in [(PLAYER_A, PLAYER_B), (PLAYER_A, PLAYER_B), (PLAYER_B, PLAYER_A)]:
        response = client.get("/api/compare", params={"player_a": player_a, "player_b": player_b})
        assert response.status_code == 200

    with SessionLocal() as db:
        rows = db.scalars(comparisons_query().order_by(Comparison.id)).all()
        assert [(row.player_a_id, row.player_b_id) for row in rows] == [
            (int(PLAYER_A), int(PLAYER_B)),
            (int(PLAYER_A), int(PLAYER_B)),
            (int(PLAYER_B), int(PLAYER_A)),
        ]
        assert all(row.compared_at.utcoffset() is not None for row in rows)


@pytest.mark.parametrize("error, status_code", [
    (comparison_service.ComparisonProfileError(ProfileStatus.not_found), 404),
    (PrivateProfileError("Private profile"), 403),
    (SteamApiError("Steam unavailable"), 502),
    (RuntimeError("Unexpected comparison failure"), 500),
])
def test_failed_comparison_not_saved(client, monkeypatch, error, status_code):
    def fail(*args):
        raise error

    monkeypatch.setattr(comparison_service, "compare_players", fail)
    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/api/compare", params={"player_a": PLAYER_A, "player_b": PLAYER_B})
    assert response.status_code == status_code
    with SessionLocal() as db:
        assert not db.scalars(comparisons_query()).all()


@pytest.mark.parametrize("steam_id", [PLAYER_A, PLAYER_B])
def test_deleting_either_player_cascades_history(steam_id):
    with SessionLocal() as db:
        comparison_id = history_service.record_comparison(db, PLAYER_A, PLAYER_B).id
        db.execute(delete(Player).where(Player.steam_id == int(steam_id)))
        db.commit()
    with SessionLocal() as db:
        assert db.get(Comparison, comparison_id) is None


@pytest.fixture
def saved_history():
    # Insert out of time order to catch accidental ordering by insertion ID.
    with SessionLocal() as db:
        rows = [
            Comparison(player_a_id=int(a), player_b_id=int(b),
                       compared_at=datetime(2020, 1, day, tzinfo=timezone.utc))
            for a, b, day in [
                (PLAYER_A, PLAYER_B, 1),
                (PLAYER_B, PLAYER_A, 3),
                (PLAYER_C, PLAYER_A, 2),
                (PLAYER_B, PLAYER_C, 4),
            ]
        ]
        db.add_all(rows)
        db.commit()
        return rows


def test_recent_comparisons_newest_first(saved_history):
    with SessionLocal() as db:
        # Include any existing real history without modifying it.
        total = len(db.scalars(select(Comparison)).all())
        records = history_service.recent_comparisons(db, limit=total)
        assert [row.compared_at for row in records] == sorted(
            (row.compared_at for row in records), reverse=True,
        )
        test_ids = {row.id for row in saved_history}
        assert [row.id for row in records if row.id in test_ids] == [
            saved_history[i].id for i in [3, 1, 2, 0]
        ]


def test_recent_comparisons_filters_by_player(saved_history):
    with SessionLocal() as db:
        records = history_service.recent_comparisons(db, PLAYER_A)
        assert [row.id for row in records] == [saved_history[i].id for i in [1, 2, 0]]
        assert history_service.recent_comparisons(db, PLAYER_A, limit=1) == records[:1]
        assert history_service.recent_comparisons(db, "76561199999999990") == []


def test_recent_opponents_groups_by_player(saved_history):
    with SessionLocal() as db:
        opponents = history_service.recent_opponents(db, PLAYER_A)
        assert [row.player.steam_id for row in opponents] == [PLAYER_B, PLAYER_C]
        assert [row.times_compared for row in opponents] == [2, 1]
        assert [row.last_compared_at for row in opponents] == [
            saved_history[i].compared_at for i in [1, 2]
        ]
        assert history_service.recent_opponents(db, PLAYER_A, limit=1) == opponents[:1]
        assert history_service.recent_opponents(db, "76561199999999990") == []


def test_read_comparisons_returns_both_profiles(client, saved_history):
    response = client.get("/api/comparisons", params={"steam_id": PLAYER_A, "limit": 2})
    assert response.status_code == 200
    data = response.json()
    assert [row["id"] for row in data] == [saved_history[i].id for i in [1, 2]]
    assert data[0] == {
        "id": saved_history[1].id,
        "compared_at": "2020-01-03T00:00:00Z",
        "player_a": {"steam_id": PLAYER_B, "persona_name": "History Player B",
                     "avatar_url": None, "profile_url": None, "visibility": 3},
        "player_b": {"steam_id": PLAYER_A, "persona_name": "History Player A",
                     "avatar_url": None, "profile_url": None, "visibility": 3},
    }
    unfiltered = client.get("/api/comparisons")
    assert unfiltered.status_code == 200
    assert len(unfiltered.json()) <= 20


def test_read_opponents_returns_profiles_counts_and_times(client, saved_history):
    response = client.get(f"/api/players/{PLAYER_A}/opponents")
    assert response.status_code == 200
    data = response.json()
    assert [row["player"]["steam_id"] for row in data] == [PLAYER_B, PLAYER_C]
    assert data[0] == {
        "player": {"steam_id": PLAYER_B, "persona_name": "History Player B",
                   "avatar_url": None, "profile_url": None, "visibility": 3},
        "last_compared_at": "2020-01-03T00:00:00Z",
        "times_compared": 2,
    }
    limited = client.get(f"/api/players/{PLAYER_A}/opponents", params={"limit": 1})
    assert limited.status_code == 200
    assert limited.json() == data[:1]


@pytest.mark.parametrize("path", [
    "/api/comparisons?steam_id=76561199999999990",
    "/api/players/76561199999999990/opponents",
])
def test_history_without_matches_returns_empty_list(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("steam_id", ["123", "abc", "765611900000000000", "7656119000000000x"])
@pytest.mark.parametrize("path", ["/api/comparisons?steam_id={}", "/api/players/{}/opponents"])
def test_history_rejects_invalid_steam_ids(client, steam_id, path):
    assert client.get(path.format(steam_id)).status_code == 422


@pytest.mark.parametrize("limit", [0, -1, 51, "abc", "1.5"])
@pytest.mark.parametrize("path", ["/api/comparisons", f"/api/players/{PLAYER_A}/opponents"])
def test_history_rejects_invalid_limits(client, limit, path):
    assert client.get(path, params={"limit": limit}).status_code == 422


@pytest.mark.parametrize("limit", [1, 50])
@pytest.mark.parametrize("path", ["/api/comparisons", f"/api/players/{PLAYER_A}/opponents"])
def test_history_accepts_limit_boundaries(client, limit, path):
    assert client.get(path, params={"limit": limit}).status_code == 200
