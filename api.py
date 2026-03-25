from flask import Blueprint, jsonify, request, abort
from app.models.db import get_db
from app.services.recommender import hybrid_recommend, content_based_scores

api = Blueprint("api", __name__, url_prefix="/api/v1")


# ─── songs ────────────────────────────────────────────────────────────────────

@api.get("/songs")
def list_songs():
    """
    List all songs with optional genre filter and pagination.
    Query params: genre, page (default 1), per_page (default 20, max 50)
    """
    genre = request.args.get("genre")
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, int(request.args.get("per_page", 20)))
    offset = (page - 1) * per_page

    conn = get_db()
    try:
        if genre:
            rows = conn.execute(
                "SELECT * FROM songs WHERE genre = ? LIMIT ? OFFSET ?",
                (genre, per_page, offset)
            ).fetchall()
            total = conn.execute(
                "SELECT COUNT(*) FROM songs WHERE genre = ?", (genre,)
            ).fetchone()[0]
        else:
            rows = conn.execute(
                "SELECT * FROM songs LIMIT ? OFFSET ?", (per_page, offset)
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM songs").fetchone()[0]

        return jsonify({
            "page": page,
            "per_page": per_page,
            "total": total,
            "songs": [dict(r) for r in rows],
        })
    finally:
        conn.close()


@api.get("/songs/<int:song_id>")
def get_song(song_id):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()
        if not row:
            abort(404, description=f"Song {song_id} not found.")
        return jsonify(dict(row))
    finally:
        conn.close()


@api.get("/songs/<int:song_id>/similar")
def similar_songs(song_id):
    """Return songs similar to the given song by audio features."""
    top_n = min(20, int(request.args.get("top_n", 10)))
    conn = get_db()
    try:
        seed = conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()
        if not seed:
            abort(404, description=f"Song {song_id} not found.")

        raw = content_based_scores(song_id, conn, top_n=top_n)
        enriched = []
        for item in raw:
            row = conn.execute(
                "SELECT id, title, artist, genre, tempo, danceability, energy, valence FROM songs WHERE id = ?",
                (item["song_id"],)
            ).fetchone()
            if row:
                enriched.append({**dict(row), "similarity_score": round(item["score"], 4)})

        return jsonify({
            "seed_song": dict(seed),
            "similar": enriched,
        })
    finally:
        conn.close()


# ─── users ────────────────────────────────────────────────────────────────────

@api.get("/users/<user_id>/history")
def user_history(user_id):
    """Return a user's listening history."""
    conn = get_db()
    try:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            abort(404, description=f"User '{user_id}' not found.")

        rows = conn.execute("""
            SELECT s.id, s.title, s.artist, s.genre,
                   i.play_count, i.liked, i.created_at
            FROM interactions i
            JOIN songs s ON s.id = i.song_id
            WHERE i.user_id = ?
            ORDER BY i.play_count DESC
        """, (user_id,)).fetchall()

        return jsonify({
            "user_id": user_id,
            "total_tracks": len(rows),
            "history": [dict(r) for r in rows],
        })
    finally:
        conn.close()


@api.post("/users/<user_id>/interactions")
def record_interaction(user_id):
    """
    Record or update a play interaction.
    Body: { "song_id": int, "liked": bool (optional) }
    """
    data = request.get_json(silent=True) or {}
    song_id = data.get("song_id")
    liked = int(bool(data.get("liked", False)))

    if not song_id:
        abort(400, description="'song_id' is required.")

    conn = get_db()
    try:
        user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            conn.execute("INSERT INTO users (id) VALUES (?)", (user_id,))

        conn.execute("""
            INSERT INTO interactions (user_id, song_id, play_count, liked)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(user_id, song_id)
            DO UPDATE SET
                play_count = play_count + 1,
                liked      = CASE WHEN excluded.liked = 1 THEN 1 ELSE liked END
        """, (user_id, song_id, liked))
        conn.commit()

        return jsonify({"status": "ok", "user_id": user_id, "song_id": song_id}), 201
    finally:
        conn.close()


# ─── recommendations ──────────────────────────────────────────────────────────

@api.get("/users/<user_id>/recommendations")
def recommend(user_id):
    """
    Return personalised song recommendations.
    Query params:
      seed_song_id  (int, optional)  — anchor a content-based signal
      top_n         (int, default 10, max 20)
      alpha         (float 0-1, default 0.5) — collaborative weight
    """
    seed_song_id = request.args.get("seed_song_id", type=int)
    top_n = min(20, int(request.args.get("top_n", 10)))
    alpha = max(0.0, min(1.0, float(request.args.get("alpha", 0.5))))

    conn = get_db()
    try:
        user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            abort(404, description=f"User '{user_id}' not found.")
    finally:
        conn.close()

    recs = hybrid_recommend(
        user_id=user_id,
        seed_song_id=seed_song_id,
        top_n=top_n,
        alpha=alpha,
    )
    return jsonify({
        "user_id": user_id,
        "seed_song_id": seed_song_id,
        "alpha": alpha,
        "recommendations": recs,
    })


# ─── genres ───────────────────────────────────────────────────────────────────

@api.get("/genres")
def list_genres():
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT genre, COUNT(*) as count FROM songs GROUP BY genre ORDER BY count DESC"
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


# ─── health ───────────────────────────────────────────────────────────────────

@api.get("/health")
def health():
    return jsonify({"status": "ok"})
