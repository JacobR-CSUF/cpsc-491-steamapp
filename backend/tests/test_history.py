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
PLAYER_IDS = [int(PLAYER_A), int(PLAYER_B)]


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
