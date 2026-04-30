"""
PhysioAssist Database Manager
- User tracking (free/paid assessments)
- Referral system with unique codes
- Points system
- Email collection
- Assessment history
"""

import sqlite3
import os
import random
import string
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "/app/physioassist.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id     INTEGER PRIMARY KEY,
        username        TEXT,
        email           TEXT,
        lang            TEXT DEFAULT 'en',
        total_assessments INTEGER DEFAULT 0,
        paid_assessments  INTEGER DEFAULT 0,
        free_used         INTEGER DEFAULT 0,
        points            INTEGER DEFAULT 0,
        referral_code     TEXT UNIQUE,
        referred_by       TEXT,
        created_at        TEXT DEFAULT (datetime('now')),
        last_active       TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS assessments (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id     INTEGER,
        lang            TEXT,
        body_region     TEXT,
        diagnosis       TEXT,
        pain_scale      INTEGER,
        paid            INTEGER DEFAULT 0,
        payment_method  TEXT,
        report_text     TEXT,
        created_at      TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(telegram_id) REFERENCES users(telegram_id)
    );

    CREATE TABLE IF NOT EXISTS referral_codes (
        code            TEXT PRIMARY KEY,
        created_by      INTEGER,
        used_by         INTEGER,
        is_used         INTEGER DEFAULT 0,
        created_at      TEXT DEFAULT (datetime('now')),
        used_at         TEXT,
        FOREIGN KEY(created_by) REFERENCES users(telegram_id)
    );

    CREATE TABLE IF NOT EXISTS share_events (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id     INTEGER,
        points_earned   INTEGER DEFAULT 10,
        new_user_id     INTEGER,
        created_at      TEXT DEFAULT (datetime('now'))
    );
    """)

    conn.commit()
    conn.close()


def generate_referral_code(telegram_id: int) -> str:
    """Generate unique 8-char referral code."""
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "PHY" + "".join(random.choices(chars, k=5))
        conn = get_conn()
        existing = conn.execute(
            "SELECT 1 FROM users WHERE referral_code=?", (code,)
        ).fetchone()
        conn.close()
        if not existing:
            return code


def get_or_create_user(telegram_id: int, username: str = "", lang: str = "en") -> dict:
    conn = get_conn()
    user = conn.execute(
        "SELECT * FROM users WHERE telegram_id=?", (telegram_id,)
    ).fetchone()

    if not user:
        code = generate_referral_code(telegram_id)
        conn.execute("""
            INSERT INTO users (telegram_id, username, lang, referral_code)
            VALUES (?, ?, ?, ?)
        """, (telegram_id, username or "", lang, code))
        conn.commit()
        user = conn.execute(
            "SELECT * FROM users WHERE telegram_id=?", (telegram_id,)
        ).fetchone()

    conn.close()
    return dict(user)


def update_user_email(telegram_id: int, email: str):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET email=? WHERE telegram_id=?", (email, telegram_id)
    )
    conn.commit()
    conn.close()


def update_user_lang(telegram_id: int, lang: str):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET lang=?, last_active=datetime('now') WHERE telegram_id=?",
        (lang, telegram_id)
    )
    conn.commit()
    conn.close()


def can_use_free(telegram_id: int) -> bool:
    """Check if user is eligible for free assessment."""
    conn = get_conn()
    user = conn.execute(
        "SELECT free_used FROM users WHERE telegram_id=?", (telegram_id,)
    ).fetchone()
    conn.close()
    if not user:
        return True
    return user["free_used"] == 0


def mark_free_used(telegram_id: int):
    conn = get_conn()
    conn.execute("""
        UPDATE users
        SET free_used=1, total_assessments=total_assessments+1,
            last_active=datetime('now')
        WHERE telegram_id=?
    """, (telegram_id,))
    conn.commit()
    conn.close()


def mark_paid(telegram_id: int, method: str = "stars"):
    conn = get_conn()
    conn.execute("""
        UPDATE users
        SET paid_assessments=paid_assessments+1,
            total_assessments=total_assessments+1,
            last_active=datetime('now')
        WHERE telegram_id=?
    """, (telegram_id,))
    conn.commit()
    conn.close()


def save_assessment(telegram_id: int, lang: str, body_region: str,
                    diagnosis: str, pain_scale: int,
                    paid: int, report_text: str):
    conn = get_conn()
    conn.execute("""
        INSERT INTO assessments
        (telegram_id, lang, body_region, diagnosis, pain_scale, paid, report_text)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (telegram_id, lang, body_region, diagnosis, pain_scale, paid, report_text))
    conn.commit()
    conn.close()


def get_user_points(telegram_id: int) -> int:
    conn = get_conn()
    user = conn.execute(
        "SELECT points FROM users WHERE telegram_id=?", (telegram_id,)
    ).fetchone()
    conn.close()
    return user["points"] if user else 0


def add_points(telegram_id: int, points: int):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET points=points+? WHERE telegram_id=?",
        (points, telegram_id)
    )
    conn.commit()
    conn.close()


def redeem_points_for_free(telegram_id: int) -> bool:
    """Spend 50 points for a free assessment. Returns True if successful."""
    conn = get_conn()
    user = conn.execute(
        "SELECT points FROM users WHERE telegram_id=?", (telegram_id,)
    ).fetchone()
    if user and user["points"] >= 50:
        conn.execute("""
            UPDATE users SET points=points-50, free_used=0
            WHERE telegram_id=?
        """, (telegram_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


def get_referral_code(telegram_id: int) -> str:
    conn = get_conn()
    user = conn.execute(
        "SELECT referral_code FROM users WHERE telegram_id=?", (telegram_id,)
    ).fetchone()
    conn.close()
    return user["referral_code"] if user else ""


def generate_one_time_code(creator_id: int) -> str:
    """Generate a one-time use free assessment code."""
    chars = string.ascii_uppercase + string.digits
    conn = get_conn()
    while True:
        code = "FREE" + "".join(random.choices(chars, k=6))
        existing = conn.execute(
            "SELECT 1 FROM referral_codes WHERE code=?", (code,)
        ).fetchone()
        if not existing:
            conn.execute("""
                INSERT INTO referral_codes (code, created_by)
                VALUES (?, ?)
            """, (code, creator_id))
            conn.commit()
            conn.close()
            return code


def use_one_time_code(code: str, user_id: int) -> bool:
    """Validate and consume a one-time code. Returns True if valid."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM referral_codes WHERE code=? AND is_used=0",
        (code,)
    ).fetchone()
    if row:
        conn.execute("""
            UPDATE referral_codes
            SET is_used=1, used_by=?, used_at=datetime('now')
            WHERE code=?
        """, (user_id, code))
        # Give creator 10 points
        conn.execute(
            "UPDATE users SET points=points+10 WHERE telegram_id=?",
            (row["created_by"],)
        )
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


def record_referral_share(sharer_id: int, new_user_id: int = None):
    """Record a share event and give points."""
    add_points(sharer_id, 10)
    conn = get_conn()
    conn.execute("""
        INSERT INTO share_events (telegram_id, new_user_id)
        VALUES (?, ?)
    """, (sharer_id, new_user_id))
    conn.commit()
    conn.close()


def process_start_referral(new_user_id: int, ref_code: str):
    """When new user starts via referral link."""
    conn = get_conn()
    referrer = conn.execute(
        "SELECT telegram_id FROM users WHERE referral_code=?", (ref_code,)
    ).fetchone()
    if referrer and referrer["telegram_id"] != new_user_id:
        # Give referrer 10 points
        conn.execute(
            "UPDATE users SET points=points+10 WHERE telegram_id=?",
            (referrer["telegram_id"],)
        )
        # Mark new user as referred
        conn.execute(
            "UPDATE users SET referred_by=? WHERE telegram_id=?",
            (ref_code, new_user_id)
        )
        conn.commit()
    conn.close()


def get_stats() -> dict:
    conn = get_conn()
    stats = {
        "total_users":       conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "total_assessments": conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0],
        "paid_assessments":  conn.execute("SELECT COUNT(*) FROM assessments WHERE paid=1").fetchone()[0],
        "emails_collected":  conn.execute("SELECT COUNT(*) FROM users WHERE email IS NOT NULL AND email != ''").fetchone()[0],
    }
    conn.close()
    return stats
