# 🎵 Music Recommendation API

A production-style REST API built with **Flask** and **NumPy** that recommends songs using a hybrid recommendation engine — combining collaborative filtering (SVD) and content-based filtering (cosine similarity on audio features).

---

## ✨ Features

- **Hybrid Recommender** — blends user behaviour signals with audio-feature similarity via a tunable `alpha` parameter
- **Collaborative Filtering** — truncated SVD on a user-item interaction matrix to surface songs liked by similar users
- **Content-Based Filtering** — cosine similarity across audio features (tempo, energy, danceability, valence, loudness, speechiness)
- **Cold-Start Handling** — new users fall back to global popularity rankings
- **RESTful API** — clean versioned endpoints (`/api/v1/...`) with pagination, filtering, and proper error handling
- **SQLite persistence** — lightweight, zero-config database seeded with 50 real-world tracks and 50 mock users

---

## 🏗 Architecture

```
music-recommender/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/
│   │   └── db.py            # SQLite connection helper
│   ├── routes/
│   │   └── api.py           # All REST endpoints
│   └── services/
│       └── recommender.py   # Core recommendation engine
├── data/
│   ├── seed.py              # Database seeding script
│   └── music.db             # Auto-generated SQLite DB
├── tests/
│   └── test_api.py          # Pytest test suite
├── run.py                   # App entrypoint
└── requirements.txt
```

---

## 🚀 Getting Started

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/music-recommender.git
cd music-recommender
pip install -r requirements.txt
```

### 2. Seed the database

```bash
python data/seed.py
```

### 3. Run the server

```bash
python run.py
# → Running on http://127.0.0.1:5000
```

---

## 📡 API Reference

### Health

```
GET /api/v1/health
```

---

### Songs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/songs` | List songs (supports `?genre=`, `?page=`, `?per_page=`) |
| `GET` | `/api/v1/songs/:id` | Get a single song |
| `GET` | `/api/v1/songs/:id/similar` | Content-based similar songs (`?top_n=`) |
| `GET` | `/api/v1/genres` | List all genres with counts |

**Example — list R&B songs:**
```bash
curl "http://localhost:5000/api/v1/songs?genre=R%26B&per_page=5"
```

**Example — find songs similar to song #1:**
```bash
curl "http://localhost:5000/api/v1/songs/1/similar?top_n=5"
```

---

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/:id/history` | User's listening history |
| `POST` | `/api/v1/users/:id/interactions` | Record a play / like |
| `GET` | `/api/v1/users/:id/recommendations` | Personalised recommendations |

**Record a play:**
```bash
curl -X POST "http://localhost:5000/api/v1/users/user_001/interactions" \
     -H "Content-Type: application/json" \
     -d '{"song_id": 3, "liked": true}'
```

**Get recommendations (hybrid, seeded from a song):**
```bash
curl "http://localhost:5000/api/v1/users/user_001/recommendations?seed_song_id=5&top_n=10&alpha=0.6"
```

#### Recommendation query parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `top_n` | int | `10` | Number of results (max 20) |
| `seed_song_id` | int | — | Optional anchor song for content arm |
| `alpha` | float | `0.5` | `0.0` = pure content-based · `1.0` = pure collaborative |

---

## 🤖 How the Recommender Works

```
User request
    │
    ├─► Collaborative Filtering (SVD)
    │       Build user-item matrix R (play_count + like bonus)
    │       Decompose: R ≈ U · Σ · Vᵀ  (k=10 latent factors)
    │       Predict scores for unseen songs
    │
    ├─► Content-Based Filtering (if seed_song_id provided)
    │       Normalise audio feature vectors
    │       Cosine similarity between seed and all songs
    │
    └─► Hybrid Blend
            score = α · collab_score + (1-α) · content_score
            Return top-N ranked songs with metadata
```

**Audio features used:** `tempo`, `danceability`, `energy`, `valence`, `loudness`, `speechiness`

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🛠 Tech Stack

- **Python 3.12**
- **Flask 3** — web framework
- **NumPy** — SVD and linear algebra for the recommendation engine
- **SQLite** — persistence (easily swappable with PostgreSQL via `psycopg2`)

---

## 📈 Potential Extensions

- Swap SQLite for **PostgreSQL** for production scale
- Add **JWT authentication** to user endpoints
- Integrate real audio features via the **Spotify Web API**
- Replace manual SVD with **implicit** library for faster ALS matrix factorisation
- Add a **Redis cache** layer for hot recommendation results
- Deploy with **Gunicorn + Docker**
