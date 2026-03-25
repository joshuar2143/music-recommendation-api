import sqlite3
import random
import os

random.seed(42)

SONGS = [
    ("Blinding Lights", "The Weeknd", "Pop", 171, 0.80, 0.65, 0.90, -4.0, 0.05),
    ("As It Was", "Harry Styles", "Pop", 174, 0.73, 0.60, 0.85, -5.3, 0.04),
    ("Stay", "The Kid LAROI & Justin Bieber", "Pop", 170, 0.75, 0.72, 0.88, -3.9, 0.03),
    ("good 4 u", "Olivia Rodrigo", "Pop-Punk", 166, 0.78, 0.70, 0.92, -4.4, 0.06),
    ("Levitating", "Dua Lipa", "Disco-Pop", 103, 0.82, 0.75, 0.88, -3.7, 0.03),
    ("Peaches", "Justin Bieber", "R&B", 90, 0.68, 0.55, 0.70, -6.0, 0.07),
    ("Montero", "Lil Nas X", "Pop-Rap", 179, 0.74, 0.58, 0.82, -5.5, 0.04),
    ("drivers license", "Olivia Rodrigo", "Pop", 143, 0.45, 0.30, 0.55, -8.1, 0.03),
    ("Heat Waves", "Glass Animals", "Indie-Pop", 80, 0.62, 0.48, 0.72, -7.0, 0.05),
    ("Watermelon Sugar", "Harry Styles", "Pop", 95, 0.79, 0.78, 0.80, -4.1, 0.04),
    ("Industry Baby", "Lil Nas X", "Hip-Hop", 150, 0.81, 0.70, 0.90, -3.2, 0.03),
    ("Butter", "BTS", "Pop", 110, 0.88, 0.80, 0.92, -3.5, 0.02),
    ("Save Your Tears", "The Weeknd", "Synth-Pop", 118, 0.73, 0.62, 0.80, -5.1, 0.04),
    ("Shivers", "Ed Sheeran", "Pop", 141, 0.86, 0.82, 0.88, -3.0, 0.03),
    ("Bad Habits", "Ed Sheeran", "Pop", 126, 0.80, 0.71, 0.84, -4.2, 0.03),
    ("Cold Heart", "Elton John & Dua Lipa", "Pop", 119, 0.77, 0.65, 0.83, -4.8, 0.04),
    ("Happier Than Ever", "Billie Eilish", "Pop", 58, 0.40, 0.25, 0.45, -9.5, 0.02),
    ("Permission to Dance", "BTS", "Pop", 124, 0.84, 0.78, 0.91, -3.3, 0.02),
    ("Solar Power", "Lorde", "Indie-Pop", 107, 0.60, 0.50, 0.68, -7.2, 0.05),
    ("Fancy Like", "Walker Hayes", "Country-Pop", 130, 0.72, 0.68, 0.78, -5.0, 0.06),
    ("Beggin", "Maneskin", "Rock", 136, 0.83, 0.77, 0.86, -3.8, 0.05),
    ("Mood", "24kGoldn", "Pop-Rap", 140, 0.76, 0.66, 0.83, -4.6, 0.04),
    ("Positions", "Ariana Grande", "R&B", 144, 0.70, 0.58, 0.74, -6.3, 0.04),
    ("34+35", "Ariana Grande", "Pop-R&B", 112, 0.72, 0.63, 0.79, -5.7, 0.05),
    ("Dynamite", "BTS", "Disco-Pop", 114, 0.89, 0.83, 0.94, -3.1, 0.02),
    ("Midnight Rain", "Taylor Swift", "Synth-Pop", 97, 0.50, 0.40, 0.60, -8.0, 0.03),
    ("Anti-Hero", "Taylor Swift", "Pop", 97, 0.64, 0.55, 0.72, -6.5, 0.03),
    ("Cruel Summer", "Taylor Swift", "Synth-Pop", 170, 0.77, 0.68, 0.84, -4.7, 0.04),
    ("Flowers", "Miley Cyrus", "Pop", 123, 0.76, 0.67, 0.82, -4.9, 0.03),
    ("Unholy", "Sam Smith & Kim Petras", "Pop", 131, 0.69, 0.60, 0.76, -5.8, 0.04),
    ("Escapism", "RAYE", "R&B", 139, 0.73, 0.64, 0.80, -5.2, 0.05),
    ("Kill Bill", "SZA", "R&B", 89, 0.55, 0.45, 0.62, -7.5, 0.04),
    ("Trustfall", "Pink", "Pop-Rock", 128, 0.74, 0.66, 0.80, -4.8, 0.05),
    ("Creepin", "Metro Boomin & The Weeknd", "R&B", 140, 0.66, 0.55, 0.74, -6.2, 0.04),
    ("Calm Down", "Rema & Selena Gomez", "Afrobeats", 106, 0.78, 0.72, 0.84, -4.3, 0.04),
    ("Essence", "Wizkid", "Afrobeats", 109, 0.75, 0.68, 0.81, -5.0, 0.05),
    ("Peru", "Fireboy DML & Ed Sheeran", "Afrobeats", 124, 0.80, 0.74, 0.85, -4.1, 0.04),
    ("Golden Hour", "JVKE", "Indie-Pop", 97, 0.63, 0.52, 0.70, -7.0, 0.04),
    ("Sunroof", "Nicky Youre & Dazy", "Indie-Pop", 120, 0.77, 0.70, 0.83, -4.5, 0.04),
    ("About Damn Time", "Lizzo", "Funk-Pop", 110, 0.86, 0.80, 0.91, -3.4, 0.03),
    ("Break My Soul", "Beyonce", "Dance-Pop", 122, 0.85, 0.79, 0.90, -3.6, 0.03),
    ("Running Up That Hill", "Kate Bush", "Synth-Pop", 104, 0.58, 0.48, 0.65, -7.8, 0.04),
    ("Numb Little Bug", "Em Beihold", "Pop", 78, 0.42, 0.30, 0.50, -9.0, 0.03),
    ("I Ain't Worried", "OneRepublic", "Pop", 136, 0.79, 0.72, 0.85, -4.4, 0.03),
    ("Electric Love", "BORNS", "Indie-Pop", 122, 0.74, 0.65, 0.80, -5.3, 0.05),
    ("Glimpse of Us", "Joji", "R&B", 69, 0.43, 0.33, 0.52, -8.8, 0.03),
    ("Ghost", "Justin Bieber", "Pop", 130, 0.68, 0.58, 0.74, -6.1, 0.04),
    ("Adore You", "Harry Styles", "Pop", 207, 0.71, 0.63, 0.78, -5.5, 0.04),
    ("Lose Control", "Teddy Swims", "Soul-Pop", 128, 0.66, 0.56, 0.73, -6.4, 0.05),
    ("Vampire", "Olivia Rodrigo", "Pop-Rock", 138, 0.65, 0.55, 0.73, -6.7, 0.04),
]

USERS = [f"user_{i:03d}" for i in range(1, 51)]

DB_PATH = os.path.join(os.path.dirname(__file__), "music.db")


def seed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
        DROP TABLE IF EXISTS songs;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS interactions;

        CREATE TABLE songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            genre TEXT NOT NULL,
            tempo REAL,
            danceability REAL,
            energy REAL,
            valence REAL,
            loudness REAL,
            speechiness REAL,
            play_count INTEGER DEFAULT 0
        );

        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            song_id INTEGER NOT NULL,
            play_count INTEGER DEFAULT 1,
            liked INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (song_id) REFERENCES songs(id),
            UNIQUE(user_id, song_id)
        );
    """)

    for song in SONGS:
        c.execute("""
            INSERT INTO songs (title, artist, genre, tempo, danceability, energy, valence, loudness, speechiness, play_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, song + (random.randint(1000, 500000),))

    for user in USERS:
        c.execute("INSERT INTO users (id) VALUES (?)", (user,))

    song_ids = [row[0] for row in c.execute("SELECT id FROM songs").fetchall()]
    for user in USERS:
        listened = random.sample(song_ids, k=random.randint(5, 20))
        for song_id in listened:
            c.execute("""
                INSERT OR IGNORE INTO interactions (user_id, song_id, play_count, liked)
                VALUES (?, ?, ?, ?)
            """, (user, song_id, random.randint(1, 30), random.randint(0, 1)))

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(SONGS)} songs and {len(USERS)} users into {DB_PATH}")


if __name__ == "__main__":
    seed()
