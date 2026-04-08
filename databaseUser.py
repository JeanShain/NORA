import sqlite3

conn = sqlite3.connect("user.db")
cursor = conn.cursor()

# таблиця користувачів
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    role TEXT DEFAULT 'user'
)
""")

conn.commit()

def add_user(user_id, username):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )
    conn.commit()


def get_user_role(user_id):
    cursor.execute(
        "SELECT role FROM users WHERE user_id = ?",
        (user_id,)
    )
    result = cursor.fetchone()

    if result:
        return result[0]
    return "user"


def set_role(user_id, role):
    cursor.execute(
        "UPDATE users SET role = ? WHERE user_id = ?",
        (role, user_id)
    )
    conn.commit()


def get_user_id_by_username(username):
    cursor.execute(
        "SELECT user_id FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()

    if result:
        return result[0]
    return None