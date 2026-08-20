import sqlite3
import os
from config import DB_FILE


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            full_name   TEXT,
            joined_at   TEXT,
            is_banned   INTEGER DEFAULT 0,
            referral_count INTEGER DEFAULT 0,
            is_verified INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_id INTEGER,
            referred_at TEXT,
            UNIQUE(referred_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS broadcast_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            message     TEXT,
            sent_at     TEXT,
            total_users INTEGER
        )
    """)

    conn.commit()
    conn.close()


def add_user(user_id: int, username: str, full_name: str):
    conn = get_connection()
    c = conn.cursor()
    from datetime import datetime
    c.execute("""
        INSERT OR IGNORE INTO users (user_id, username, full_name, joined_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, full_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def is_banned(user_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row["is_banned"]) if row else False


def ban_user(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def unban_user(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE is_banned = 0")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_count() -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM users")
    row = c.fetchone()
    conn.close()
    return row["cnt"]


def add_referral(referrer_id: int, referred_id: int) -> bool:
    """Returns True if referral was new (not duplicate)."""
    conn = get_connection()
    c = conn.cursor()
    from datetime import datetime
    try:
        c.execute("""
            INSERT INTO referrals (referrer_id, referred_id, referred_at)
            VALUES (?, ?, ?)
        """, (referrer_id, referred_id, datetime.now().isoformat()))
        # Increment referrer count
        c.execute("UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?", (referrer_id,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_referral_count(user_id: int) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT referral_count FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row["referral_count"] if row else 0


def is_verified(user_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT is_verified FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row["is_verified"]) if row else False


def set_verified(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_verified = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
