import sqlite3


def get_connection():
    return sqlite3.connect('music.db')


# add new album
def add_album(album_id, title):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT OR IGNORE INTO albums (id, title) VALUES (?, ?)',
        (album_id, title)
    )

    conn.commit()
    conn.close()


# add new song to album
def add_song(song_id, title, file_id, album_id, thumbnail):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT OR IGNORE INTO songs (id, title, file_id, album_id, thumbnail) VALUES (?, ?, ?, ?, ?)',
        (song_id, title, file_id, album_id, thumbnail)
    )

    conn.commit()
    conn.close()


# get all songs in album
def get_songs_by_album(album_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT id, title, file_id FROM songs WHERE album_id = ? ORDER BY id',
        (album_id,)
    )

    songs = cursor.fetchall()
    conn.close()

    return songs

# get 1 song
def get_song(song_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT title, file_id, thumbnail FROM songs WHERE id = ?',
        (song_id,)
    )

    songs = cursor.fetchone()
    conn.close()

    return songs

# for SECRETROOM
def get_random_songs(limit=20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, file_id FROM songs ORDER BY RANDOM() LIMIT ?",
        (limit,)
    )

    songs = cursor.fetchall()
    conn.close()

    return songs