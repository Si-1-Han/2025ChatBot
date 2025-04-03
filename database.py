import sqlite3
import os

DB_PATH = "chatbot.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 수동 호출용 초기화 함수 (원할 때만 실행)
def init_db():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            message TEXT,
            response TEXT,
            FOREIGN KEY (chat_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        )
    """)

    db.commit()
    db.close()

# CREATE
def create_chat(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO chat_sessions (user_id) VALUES (?)", (user_id,))
    db.commit()
    chat_id = cur.lastrowid
    db.close()
    return chat_id

def save_message(chat_id, message, response):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO messages (chat_id, message, response) VALUES (?, ?, ?)",
        (chat_id, message, response)
    )
    db.commit()
    db.close()

# READ
def get_chat_list(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT cs.id, m.message
        FROM chat_sessions cs
        LEFT JOIN messages m ON cs.id = m.chat_id
        WHERE cs.user_id = ?
        GROUP BY cs.id
        ORDER BY cs.id DESC
    """, (user_id,))
    chats = [{"id": row["id"], "title": row["message"][:20] if row["message"] else "(빈 대화)"} for row in cur.fetchall()]
    db.close()
    return chats

def get_chat_history_by_chat_id(chat_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT message, response FROM messages WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
    messages = [{"message": row["message"], "response": row["response"]} for row in cur.fetchall()]
    db.close()
    return messages

# UPDATE (optional)
def update_message(message_id, new_message, new_response):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE messages SET message = ?, response = ? WHERE id = ?",
        (new_message, new_response, message_id)
    )
    db.commit()
    db.close()

# DELETE
def delete_chat(chat_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    cur.execute("DELETE FROM chat_sessions WHERE id = ?", (chat_id,))
    db.commit()
    db.close()
