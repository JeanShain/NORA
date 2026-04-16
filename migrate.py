import sqlite3
import psycopg2
import os

DATABASE_URL = "postgresql://postgres.fhvgeftyqiuhnblmvcan:miwWir-6cuzry-vifmex@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"

# ===== ПІДКЛЮЧЕННЯ =====

pg_conn = psycopg2.connect(DATABASE_URL)
pg_cur = pg_conn.cursor()

# ===== SONGS =====

try:
    sqlite_conn = sqlite3.connect("music.db")
    sqlite_cur = sqlite_conn.cursor()

    sqlite_cur.execute("SELECT id, title, file_id, album_id, thumbnail FROM songs")
    songs = sqlite_cur.fetchall()

    print(f"Songs found: {len(songs)}")

    for song in songs:
        pg_cur.execute("""
        INSERT INTO songs (song_id, title, file_id, album_id, thumbnail)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (song_id) DO NOTHING
        """, song)

    pg_conn.commit()

except Exception as e:
    print("Songs error:", e)



pg_cur.close()
pg_conn.close()

print("MIGRATION DONE!!!")