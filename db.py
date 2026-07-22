import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        username TEXT,
        role TEXT DEFAULT 'user'
    )
    """)

    # SONGS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        song_id TEXT PRIMARY KEY,
        title TEXT,
        file_id TEXT,
        album_id TEXT,
        thumbnail TEXT
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

# ===== USER ============================

def add_user(user_id, username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users (user_id, username)
    VALUES (%s, %s)
    ON CONFLICT (user_id) DO NOTHING
    """, (user_id, username))

    conn.commit()
    cur.close()
    conn.close()


def get_user_role(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT role FROM users WHERE user_id=%s", (user_id,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0] if result else "user"


def set_role(user_id, role):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users (user_id, role)
    VALUES (%s, %s)
    ON CONFLICT (user_id)
    DO UPDATE SET role=EXCLUDED.role
    """, (user_id, role))

    conn.commit()
    cur.close()
    conn.close()


def get_user_id_by_username(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT user_id FROM users WHERE LOWER(username)=%s",
        (username.lower(),)
    )
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0] if result else None


def get_all_users():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT user_id, username, role FROM users")
    users = cur.fetchall()

    cur.close()
    conn.close()

    return users
# =======================================

# ===== SONG ============================

def add_song(song_id, title, file_id, album_id, thumbnail):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO songs (song_id, title, file_id, album_id, thumbnail)
    VALUES (%s, %s, %s, %s, %s)
    """, (song_id, title, file_id, album_id, thumbnail))

    conn.commit()
    cur.close()
    conn.close()


def get_songs_by_album(album_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT song_id, title, file_id
    FROM songs
    WHERE album_id=%s
    """, (album_id,))

    songs = cur.fetchall()

    cur.close()
    conn.close()

    return songs


def get_song(song_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT title, file_id, thumbnail
    FROM songs
    WHERE song_id=%s
    """, (song_id,))

    song = cur.fetchone()

    cur.close()
    conn.close()

    return song


def get_random_songs(limit=10):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT song_id, title, file_id
    FROM songs
    ORDER BY RANDOM()
    LIMIT %s
    """, (limit,))

    songs = cur.fetchall()

    cur.close()
    conn.close()

    return songs














