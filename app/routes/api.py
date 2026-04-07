from flask import Blueprint, jsonify, request, abort, render_template, redirect, url_for
from app.models.db import get_db
from app.services.recommender import hybrid_recommend, content_based_scores

api = Blueprint("api", __name__, url_prefix="/api/v1")


def _load_songs_page(genre, page, per_page, search=None, sort_by="id", sort_dir="asc"):
    offset = (page - 1) * per_page
    conn = get_db()
    try:
        allowed_sort = {"id", "title", "artist", "genre", "tempo", "danceability", "energy", "valence"}
        sort_by = sort_by if sort_by in allowed_sort else "id"
        sort_dir = "desc" if sort_dir.lower() == "desc" else "asc"

        where_clauses = []
        params = []
        if genre:
            where_clauses.append("genre = ?")
            params.append(genre)
        if search:
            where_clauses.append("(title LIKE ? OR artist LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

        where = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        rows = conn.execute(
            f"SELECT * FROM songs{where} ORDER BY {sort_by} {sort_dir} LIMIT ? OFFSET ?",
            (*params, per_page, offset)
        ).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) FROM songs{where}",
            tuple(params)
        ).fetchone()[0]

        return [dict(r) for r in rows], total
    finally:
        conn.close()


def _get_song(song_id):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def _load_user_history(user_id):
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT s.id, s.title, s.artist, s.genre,
                   i.play_count, i.liked, i.created_at
            FROM interactions i
            JOIN songs s ON s.id = i.song_id
            WHERE i.user_id = ?
            ORDER BY i.play_count DESC
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _load_genres():
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT genre, COUNT(*) as count FROM songs GROUP BY genre ORDER BY count DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _load_totals():
    conn = get_db()
    try:
        total_songs = conn.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        return total_songs, total_users
    finally:
        conn.close()


# ─── songs ────────────────────────────────────────────────────────────────────

@api.get("/songs")
def list_songs():
    """
    List all songs, including an optional genre filter, search, sorting, and pages.
    Query params: genre, search, sort_by, sort_dir, page (default 1), per_page (default 20, max 100)
    """
    genre = request.args.get("genre")
    search = request.args.get("search", "").strip() or None
    sort_by = request.args.get("sort_by", "id")
    sort_dir = request.args.get("sort_dir", "asc")
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(100, int(request.args.get("per_page", 20)))

    songs, total = _load_songs_page(
        genre,
        page,
        per_page,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": total,
        "songs": songs,
    })


@api.get("/songs/ui")
def songs_page():
    genre = request.args.get("genre", "")
    search = request.args.get("search", "")
    sort_by = request.args.get("sort_by", "id")
    sort_dir = request.args.get("sort_dir", "asc")
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(100, int(request.args.get("per_page", 20)))

    songs, total = _load_songs_page(
        genre,
        page,
        per_page,
        search=search or None,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return render_template(
        "songs.html",
        page=page,
        per_page=per_page,
        total=total,
        songs=songs,
        genre=genre,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@api.get("/songs/ui/fragment")
def songs_table_fragment():
    genre = request.args.get("genre", "")
    search = request.args.get("search", "")
    sort_by = request.args.get("sort_by", "id")
    sort_dir = request.args.get("sort_dir", "asc")
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(100, int(request.args.get("per_page", 20)))

    songs, total = _load_songs_page(
        genre,
        page,
        per_page,
        search=search or None,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return render_template(
        "_songs_table.html",
        page=page,
        per_page=per_page,
        total=total,
        songs=songs,
        genre=genre,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@api.get("/ui")
def ui_dashboard():
    total_songs, total_users = _load_totals()
    genres = _load_genres()
    return render_template(
        "dashboard.html",
        total_songs=total_songs,
        total_users=total_users,
        genres=genres,
    )


@api.get("/songs/<int:song_id>/ui")
def song_detail_page(song_id):
    song = _get_song(song_id)
    if not song:
        abort(404, description=f"Song {song_id} not found.")

    conn = get_db()
    try:
        raw = content_based_scores(song_id, conn, top_n=10)
        similar = []
        for item in raw:
            row = conn.execute(
                "SELECT id, title, artist, genre, tempo, danceability, energy, valence FROM songs WHERE id = ?",
                (item["song_id"],)
            ).fetchone()
            if row:
                similar.append({**dict(row), "similarity_score": round(item["score"], 4)})
    finally:
        conn.close()

    return render_template("song_detail.html", song=song, similar=similar)


@api.get("/users/<user_id>/history/ui")
def user_history_page(user_id):
    status = request.args.get("status")
    history = _load_user_history(user_id)
    return render_template(
        "user_history.html",
        user_id=user_id,
        history=history,
        status=status,
    )


@api.post("/users/<user_id>/interactions/ui")
def record_interaction_ui(user_id):
    song_id = request.form.get("song_id")
    liked = bool(request.form.get("liked"))

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
        """, (user_id, song_id, int(liked)))
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("api.user_history_page", user_id=user_id, status="saved"))


@api.get("/users/<user_id>/recommendations/ui")
def recommendations_page(user_id):
    seed_song_id = request.args.get("seed_song_id", type=int)
    seed_title = request.args.get("seed_title", "").strip()
    top_n = min(20, int(request.args.get("top_n", 10)))
    alpha = max(0.0, min(1.0, float(request.args.get("alpha", 0.5))))

    # If seed_title is provided, look up the song and use its ID
    if seed_title and not seed_song_id:
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT id FROM songs WHERE LOWER(title) LIKE LOWER(?) LIMIT 1",
                (f"%{seed_title}%",)
            ).fetchone()
            if row:
                seed_song_id = row[0]
        finally:
            conn.close()

    recs = hybrid_recommend(
        user_id=user_id,
        seed_song_id=seed_song_id,
        top_n=top_n,
        alpha=alpha,
    )

    return render_template(
        "recommendations.html",
        user_id=user_id,
        seed_song_id=seed_song_id,
        seed_title=seed_title,
        alpha=alpha,
        recommendations=recs,
    )


@api.get("/genres/ui")
def list_genres_page():
    genres = _load_genres()
    return render_template("genres.html", genres=genres)


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
      seed_title    (string, optional) — search for song title to use as seed
      top_n         (int, default 10, max 20)
      alpha         (float 0-1, default 0.5) — collaborative weight
    """
    seed_song_id = request.args.get("seed_song_id", type=int)
    seed_title = request.args.get("seed_title", "").strip()
    top_n = min(20, int(request.args.get("top_n", 10)))
    alpha = max(0.0, min(1.0, float(request.args.get("alpha", 0.5))))

    conn = get_db()
    try:
        user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            abort(404, description=f"User '{user_id}' not found.")
        
        # If seed_title is provided, look up the song and use its ID
        if seed_title and not seed_song_id:
            row = conn.execute(
                "SELECT id FROM songs WHERE LOWER(title) LIKE LOWER(?) LIMIT 1",
                (f"%{seed_title}%",)
            ).fetchone()
            if row:
                seed_song_id = row[0]
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
        "seed_title": seed_title,
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
