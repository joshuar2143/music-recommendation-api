"""
Recommendation engine using both a 
  - Content-Based Filtering through a cosine similarity on audio features
  - Collaborative Filtering using a user-item matrix factorisation (SVD via numpy)
"""

import numpy as np
from app.models.db import get_db

""" Audio features have been chosen based off of spotify recommendation values """

AUDIO_FEATURES = ["tempo", "danceability", "energy", "valence", "loudness", "speechiness"]


# ─── helpers ──────────────────────────────────────────────────────────────────

def _normalise(matrix: np.ndarray) -> np.ndarray:
    """normalise every column so features are on the same scale on a scale of 0 to 1"""
    mins = matrix.min(axis=0)
    maxs = matrix.max(axis=0)
    ranges = np.where((maxs - mins) == 0, 1, maxs - mins)
    return (matrix - mins) / ranges


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Return cosine similarity between vector a and every row in matrix b."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b, axis=1)
    denom = np.where(norm_b == 0, 1e-10, norm_b)
    return b.dot(a) / (norm_a * denom + 1e-10)


# ─── data loaders ─────────────────────────────────────────────────────────────

def _load_songs(conn):
    rows = conn.execute(
        f"SELECT id, title, artist, genre, {', '.join(AUDIO_FEATURES)}, play_count FROM songs"
    ).fetchall()
    return rows


def _load_interactions(conn):
    return conn.execute(
        "SELECT user_id, song_id, play_count, liked FROM interactions"
    ).fetchall()


# ─── content-based filtering ──────────────────────────────────────────────────

def content_based_scores(song_id: int, conn, top_n: int = 20) -> list[dict]:
    """
    Score every song by audio-feature similarity to the given seed song.
    Returns a ranked list of dicts  {song_id, score}.
    """
    songs = _load_songs(conn)
    id_to_idx = {s["id"]: i for i, s in enumerate(songs)}

    if song_id not in id_to_idx:
        return []

    feature_matrix = np.array(
        [[s[f] for f in AUDIO_FEATURES] for s in songs], dtype=float
    )
    feature_matrix = _normalise(feature_matrix)

    seed_vec = feature_matrix[id_to_idx[song_id]]
    scores = _cosine_similarity(seed_vec, feature_matrix)

    results = [
        {"song_id": songs[i]["id"], "score": float(scores[i])}
        for i in range(len(songs))
        if songs[i]["id"] != song_id
    ]
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


# ─── collaborative filtering (SVD) ────────────────────────────────────────────

def collaborative_scores(user_id: str, conn, top_n: int = 20) -> list[dict]:
    """
    Build a user-item matrix, decompose with truncated SVD, and return
    predicted scores for songs the user has not yet interacted with.
    """
    songs = _load_songs(conn)
    interactions = _load_interactions(conn)

    all_users = sorted({r["user_id"] for r in interactions})
    all_songs = [s["id"] for s in songs]

    if user_id not in all_users:
        # cold-start: return top global songs by play_count
        ranked = sorted(songs, key=lambda s: s["play_count"], reverse=True)
        return [{"song_id": s["id"], "score": float(s["play_count"])} for s in ranked[:top_n]]

    user_idx = {u: i for i, u in enumerate(all_users)}
    song_idx = {s: i for i, s in enumerate(all_songs)}

    R = np.zeros((len(all_users), len(all_songs)), dtype=float)
    listened_song_ids = set()
    for r in interactions:
        ui = user_idx[r["user_id"]]
        si = song_idx[r["song_id"]]
        # weight = plays + bonus for likes
        R[ui, si] = r["play_count"] + (5.0 if r["liked"] else 0.0)
        if r["user_id"] == user_id:
            listened_song_ids.add(r["song_id"])

    # truncated SVD  (k=10 latent factors)
    k = min(10, min(R.shape) - 1)
    U, sigma, Vt = np.linalg.svd(R, full_matrices=False)
    U_k = U[:, :k]
    sigma_k = np.diag(sigma[:k])
    Vt_k = Vt[:k, :]

    R_hat = U_k @ sigma_k @ Vt_k

    uid = user_idx[user_id]
    results = [
        {"song_id": all_songs[si], "score": float(R_hat[uid, si])}
        for si in range(len(all_songs))
        if all_songs[si] not in listened_song_ids
    ]
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


# ─── hybrid recommender ────────────────────────────────────────────────────────

def hybrid_recommend(
    user_id: str,
    seed_song_id: int | None = None,
    top_n: int = 10,
    alpha: float = 0.5,          # weight for collaborative score
) -> list[dict]:
    """
    Hybrid recommendation blending content-based and collaborative signals.

    Parameters
    ----------
    user_id     : target user
    seed_song_id: optional anchor song for content-based arm
    top_n       : number of results
    alpha       : 0 = pure content-based, 1 = pure collaborative
    """
    conn = get_db()

    try:
        collab = collaborative_scores(user_id, conn, top_n=50)
        collab_map = {r["song_id"]: r["score"] for r in collab}

        if seed_song_id:
            content = content_based_scores(seed_song_id, conn, top_n=50)
            content_map = {r["song_id"]: r["score"] for r in content}
        else:
            content_map = {}

        # normalise each score set to [0, 1]
        def _norm_map(m):
            if not m:
                return m
            vals = np.array(list(m.values()), dtype=float)
            mn, mx = vals.min(), vals.max()
            span = mx - mn if mx != mn else 1.0
            return {k: (v - mn) / span for k, v in m.items()}

        collab_map = _norm_map(collab_map)
        content_map = _norm_map(content_map)

        candidate_ids = set(collab_map) | set(content_map)

        blended = {}
        for sid in candidate_ids:
            c_score = collab_map.get(sid, 0.0)
            cb_score = content_map.get(sid, 0.0)
            if seed_song_id and content_map:
                blended[sid] = alpha * c_score + (1 - alpha) * cb_score
            else:
                blended[sid] = c_score

        ranked_ids = sorted(blended, key=lambda x: blended[x], reverse=True)[:top_n]

        # enrich with song metadata
        results = []
        for sid in ranked_ids:
            row = conn.execute(
                "SELECT id, title, artist, genre, tempo, danceability, energy, valence, play_count FROM songs WHERE id = ?",
                (sid,)
            ).fetchone()
            if row:
                results.append({
                    "song_id": row["id"],
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "audio_features": {
                        "tempo": row["tempo"],
                        "danceability": row["danceability"],
                        "energy": row["energy"],
                        "valence": row["valence"],
                    },
                    "play_count": row["play_count"],
                    "recommendation_score": round(blended[sid], 4),
                })
        return results

    finally:
        conn.close()
