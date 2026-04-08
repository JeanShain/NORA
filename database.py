import sqlite3

conn = sqlite3.connect('music.db')
cursor = conn.cursor()

# album
cursor.execute('''
               CREATE TABLE IF NOT EXISTS albums
               (
                   id
                   TEXT
                   PRIMARY
                   KEY,
                   title
                   TEXT
               )
               ''')

# songs
cursor.execute("""
CREATE TABLE IF NOT EXISTS songs (
    id TEXT PRIMARY KEY,
    title TEXT,
    file_id TEXT,
    album_id TEXT,
    thumbnail TEXT
)
""")

conn.commit()
conn.close()