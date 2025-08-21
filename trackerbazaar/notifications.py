import sqlite3
from datetime import datetime

DB_FILE = "trackerbazaar_v2.db"  # ✅ new DB

def init_notifications_table():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                read INTEGER DEFAULT 0
            )
        """)
        conn.commit()

def add_notification(email, message):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO notifications (email, message, timestamp) VALUES (?,?,?)",
            (email, message, datetime.now().isoformat())
        )
        conn.commit()

def get_notifications(email, unread_only=False):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        if unread_only:
            c.execute("SELECT id, message, timestamp FROM notifications WHERE email=? AND read=0 ORDER BY id DESC", (email,))
        else:
            c.execute("SELECT id, message, timestamp, read FROM notifications WHERE email=? ORDER BY id DESC", (email,))
        return c.fetchall()

def mark_as_read(notification_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE notifications SET read=1 WHERE id=?", (notification_id,))
        conn.commit()

# Initialize
init_notifications_table()
