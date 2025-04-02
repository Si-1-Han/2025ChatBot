import sqlite3
from datetime import datetime
import os
import config

DB_PATH = config.DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            message TEXT,
            response TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_conversation(user_id, message, response):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO conversations (user_id, message, response, timestamp) VALUES (?, ?, ?, ?)',
              (user_id, message, response, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_conversation_history(user_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT message, response FROM conversations WHERE user_id = ? ORDER BY id DESC LIMIT ?', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows[::-1]  # 최신 → 과거 순 정렬 후 뒤집기

def clear_conversation_history(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM conversations WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# 앱 실행 시 자동 DB 초기화
if not os.path.exists(DB_PATH):
    init_db()
