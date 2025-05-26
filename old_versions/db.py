import sqlite3

def init_db():
    conn = sqlite3.connect("core_db.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message(user_id, role, content):
    conn = sqlite3.connect("core_db.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    conn.close()

def get_user_history(user_id, max_messages=10):
    conn = sqlite3.connect("core_db.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, max_messages))
    rows = cursor.fetchall()
    conn.close()
    # Reverter para ordem cronológica
    return [{"role": role, "content": content} for role, content in reversed(rows)]

def clear_user_history(user_id):
    conn = sqlite3.connect("core_db.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
