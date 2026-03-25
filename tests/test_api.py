import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from data.seed import seed, DB_PATH


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Seed a fresh test database once per session."""
    seed()
    yield


@pytest.fixture()
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as c:
        yield c


# ─── health ───────────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


# ─── songs ────────────────────────────────────────────────────────────────────

def test_list_songs_default(client):
    r = client.get("/api/v1/songs")
    assert r.status_code == 200
    data = r.get_json()
    assert "songs" in data
    assert len(data["songs"]) <= 20


def test_list_songs_genre_filter(client):
    r = client.get("/api/v1/songs?genre=R%26B")
    assert r.status_code == 200
    data = r.get_json()
    for song in data["songs"]:
        assert song["genre"] == "R&B"


def test_get_song(client):
    r = client.get("/api/v1/songs/1")
    assert r.status_code == 200
    data = r.get_json()
    assert "title" in data and "artist" in data


def test_get_song_not_found(client):
    r = client.get("/api/v1/songs/9999")
    assert r.status_code == 404


def test_similar_songs(client):
    r = client.get("/api/v1/songs/1/similar?top_n=5")
    assert r.status_code == 200
    data = r.get_json()
    assert "similar" in data
    assert len(data["similar"]) <= 5
    for s in data["similar"]:
        assert "similarity_score" in s
        assert s["id"] != 1


# ─── genres ───────────────────────────────────────────────────────────────────

def test_list_genres(client):
    r = client.get("/api/v1/genres")
    assert r.status_code == 200
    genres = r.get_json()
    assert isinstance(genres, list)
    assert all("genre" in g and "count" in g for g in genres)


# ─── user history ─────────────────────────────────────────────────────────────

def test_user_history(client):
    r = client.get("/api/v1/users/user_001/history")
    assert r.status_code == 200
    data = r.get_json()
    assert "history" in data
    assert data["user_id"] == "user_001"


def test_user_history_not_found(client):
    r = client.get("/api/v1/users/ghost_user/history")
    assert r.status_code == 404


# ─── interactions ─────────────────────────────────────────────────────────────

def test_record_interaction(client):
    r = client.post(
        "/api/v1/users/user_001/interactions",
        json={"song_id": 1, "liked": True},
    )
    assert r.status_code == 201
    data = r.get_json()
    assert data["status"] == "ok"


def test_record_interaction_missing_song_id(client):
    r = client.post("/api/v1/users/user_001/interactions", json={})
    assert r.status_code == 400


def test_new_user_interaction(client):
    """Creating an interaction for a brand-new user should work (auto-creates user)."""
    r = client.post(
        "/api/v1/users/brand_new_user/interactions",
        json={"song_id": 2},
    )
    assert r.status_code == 201


# ─── recommendations ──────────────────────────────────────────────────────────

def test_recommendations_known_user(client):
    r = client.get("/api/v1/users/user_001/recommendations?top_n=5")
    assert r.status_code == 200
    data = r.get_json()
    assert "recommendations" in data
    assert len(data["recommendations"]) <= 5
    for rec in data["recommendations"]:
        assert "recommendation_score" in rec
        assert "title" in rec


def test_recommendations_with_seed(client):
    r = client.get("/api/v1/users/user_001/recommendations?seed_song_id=1&top_n=5")
    assert r.status_code == 200
    data = r.get_json()
    assert data["seed_song_id"] == 1
    assert len(data["recommendations"]) <= 5


def test_recommendations_cold_start(client):
    """A brand new user should still get recommendations (global popularity fallback)."""
    r = client.get("/api/v1/users/cold_start_user/recommendations")
    assert r.status_code == 404   # user must exist first


def test_recommendations_alpha_boundary(client):
    r = client.get("/api/v1/users/user_001/recommendations?alpha=0.0&top_n=5")
    assert r.status_code == 200
    r2 = client.get("/api/v1/users/user_001/recommendations?alpha=1.0&top_n=5")
    assert r2.status_code == 200
