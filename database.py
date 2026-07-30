# ============================================================
#  database.py — Your Storage Room (PostgreSQL / Supabase)
#  CORRECTED VERSION — see CODE_REVIEW_REPORT.md for the diff
#  summary of every change made in this file.
# ============================================================

import os
import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Add it to your .env / Render environment."
    )

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=int(os.getenv("DB_POOL_MAX", "10")),
            dsn=DATABASE_URL,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
    return _pool


class _PooledConnection:
    def __init__(self, raw_conn):
        self._raw = raw_conn
        for attr in ("cursor", "commit", "rollback"):
            setattr(self, attr, getattr(raw_conn, attr))

    def close(self):
        # Reset the connection before it goes back to the pool. If a query
        # failed somewhere and nobody explicitly called rollback(), the
        # connection could go back to the pool "poisoned" — still sitting
        # inside a failed transaction. rollback() is a no-op (harmless) if
        # there was nothing to undo.
        try:
            self._raw.rollback()
            _get_pool().putconn(self._raw)
        except Exception:
            # rollback() itself failed — the connection is actually dead
            # (network blip, Supabase restart, etc.), not just mid-task.
            # Tell the pool to discard it instead of handing a broken
            # connection to the next unrelated request. The pool will
            # simply open a fresh one next time it's needed.
            try:
                _get_pool().putconn(self._raw, close=True)
            except Exception:
                pass


def get_db():
    return _PooledConnection(_get_pool().getconn())


# ══════════════════════════════════════════════════
#  1. INIT: Create all tables + indexes if they don't exist
# ══════════════════════════════════════════════════
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            SERIAL PRIMARY KEY,
                email         TEXT    UNIQUE NOT NULL,
                name          TEXT,
                picture       TEXT,
                access_token  TEXT,
                refresh_token TEXT,
                created_at    TIMESTAMP DEFAULT NOW(),
                last_login    TIMESTAMP DEFAULT NOW()
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id            SERIAL PRIMARY KEY,
                gmail_id      TEXT    NOT NULL,
                user_email    TEXT    NOT NULL,
                subject       TEXT    DEFAULT '(No Subject)',
                sender        TEXT,
                sender_email  TEXT,
                snippet       TEXT,
                body          TEXT,
                date          TIMESTAMP,
                is_read       BOOLEAN DEFAULT FALSE,
                priority      TEXT    DEFAULT 'medium',
                category      TEXT    DEFAULT 'Other',
                ai_summary    TEXT,
                fetched_at    TIMESTAMP DEFAULT NOW(),

                UNIQUE(gmail_id, user_email)
            )
        """)

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_emails_user_email ON emails(user_email)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_emails_user_date "
            "ON emails(user_email, date DESC)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_emails_user_priority "
            "ON emails(user_email, priority)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_emails_user_category "
            "ON emails(user_email, category)"
        )

        conn.commit()
        print(f"✅ Database ready (PostgreSQL / Supabase)")
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════
#  2. USER FUNCTIONS
# ══════════════════════════════════════════════════

def create_or_update_user(email: str, name: str, picture: str,
                           access_token: str, refresh_token: str = None):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (email, name, picture, access_token, refresh_token, last_login)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON CONFLICT(email) DO UPDATE SET
                name          = EXCLUDED.name,
                picture       = EXCLUDED.picture,
                access_token  = EXCLUDED.access_token,
                refresh_token = COALESCE(EXCLUDED.refresh_token, users.refresh_token),
                last_login    = NOW()
        """, (email, name, picture, access_token, refresh_token))
        conn.commit()
        print(f"✅ User saved: {email}")
    except Exception as e:
        print(f"❌ Error saving user: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email: str):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        conn.commit()  # closes out the read transaction cleanly instead of
                        # leaving it open when the connection returns to the pool
        return dict(row) if row else None
    finally:
        cursor.close()
        conn.close()


def update_access_token(email: str, access_token: str):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET access_token = %s WHERE email = %s",
            (access_token, email)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════
#  3. EMAIL FUNCTIONS
# ══════════════════════════════════════════════════

def save_email(email_data: dict):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO emails
                (gmail_id, user_email, subject, sender, sender_email,
                 snippet, body, date, is_read, priority, category, ai_summary)
            VALUES
                (%(gmail_id)s, %(user_email)s, %(subject)s, %(sender)s, %(sender_email)s,
                 %(snippet)s, %(body)s, %(date)s, %(is_read)s, %(priority)s, %(category)s, %(ai_summary)s)
            ON CONFLICT (gmail_id, user_email) DO NOTHING
        """, email_data)
        conn.commit()
    except Exception as e:
        print(f"❌ Error saving email {email_data.get('gmail_id')}: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def save_emails_bulk(emails_list: list):
    if not emails_list:
        return

    conn = get_db()
    cursor = conn.cursor()
    saved_count = 0
    try:
        for email_data in emails_list:
            try:
                cursor.execute("""
                    INSERT INTO emails
                        (gmail_id, user_email, subject, sender, sender_email,
                         snippet, body, date, is_read, priority, category, ai_summary)
                    VALUES
                        (%(gmail_id)s, %(user_email)s, %(subject)s, %(sender)s, %(sender_email)s,
                         %(snippet)s, %(body)s, %(date)s, %(is_read)s, %(priority)s, %(category)s, %(ai_summary)s)
                    ON CONFLICT (gmail_id, user_email) DO NOTHING
                """, email_data)
                saved_count += 1
            except Exception as e:
                print(f"⚠️  Skipped email {email_data.get('gmail_id')}: {e}")
        conn.commit()
        print(f"✅ Saved {saved_count}/{len(emails_list)} emails to database")
    except Exception as e:
        print(f"❌ Bulk save failed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def replace_all_emails_for_user(user_email: str, emails_list: list):
    """
    Atomically replaces ALL of a user's emails with a fresh batch.
    Runs as ONE transaction — this is exactly why we do NOT set
    autocommit=True globally on the pool (see note in _get_pool):
    doing so would make the DELETE below commit instantly, and the
    rollback on failure would have nothing left to undo.
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM emails WHERE user_email = %s", (user_email,))

        for email_data in emails_list:
            cursor.execute("""
                INSERT INTO emails
                    (gmail_id, user_email, subject, sender, sender_email,
                     snippet, body, date, is_read, priority, category, ai_summary)
                VALUES
                    (%(gmail_id)s, %(user_email)s, %(subject)s, %(sender)s, %(sender_email)s,
                     %(snippet)s, %(body)s, %(date)s, %(is_read)s, %(priority)s, %(category)s, %(ai_summary)s)
                ON CONFLICT (gmail_id, user_email) DO NOTHING
            """, email_data)

        conn.commit()
        print(f"🔄 Replaced emails for {user_email}: {len(emails_list)} saved")
        return True
    except Exception as e:
        print(f"❌ Replace failed, rolling back — old data kept: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_emails_for_user(user_email: str, limit: int = 50):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM emails
            WHERE user_email = %s
            ORDER BY date DESC, fetched_at DESC
            LIMIT %s
        """, (user_email, limit))
        rows = cursor.fetchall()
        conn.commit()
        return [dict(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


def get_existing_gmail_ids(user_email: str) -> set:
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT gmail_id FROM emails WHERE user_email = %s", (user_email,)
        )
        rows = cursor.fetchall()
        conn.commit()
        return {row["gmail_id"] for row in rows}
    finally:
        cursor.close()
        conn.close()


def get_email_by_id(gmail_id: str, user_email: str):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM emails
            WHERE gmail_id = %s AND user_email = %s
        """, (gmail_id, user_email))
        row = cursor.fetchone()
        conn.commit()
        return dict(row) if row else None
    finally:
        cursor.close()
        conn.close()


def mark_email_as_read(gmail_id: str, user_email: str):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE emails SET is_read = TRUE WHERE gmail_id = %s AND user_email = %s",
            (gmail_id, user_email)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


_ALLOWED_PRIORITIES = {"high", "medium", "low"}
_ALLOWED_CATEGORIES = {"Work", "Finance", "Promotions", "Social", "Newsletters", "Other"}


def get_filtered_emails(user_email: str, priority: str = None,
                         category: str = None, read_status: str = None):
    conn = get_db()
    cursor = conn.cursor()
    try:
        query  = "SELECT * FROM emails WHERE user_email = %s"
        params = [user_email]

        if priority and priority.lower() in _ALLOWED_PRIORITIES:
            query += " AND priority = %s"
            params.append(priority.lower())

        if category and category in _ALLOWED_CATEGORIES:
            query += " AND category = %s"
            params.append(category)

        if read_status == "unread":
            query += " AND is_read = FALSE"
        elif read_status == "read":
            query += " AND is_read = TRUE"

        query += " ORDER BY date DESC LIMIT 50"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.commit()
        return [dict(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


def delete_emails_for_user(user_email: str):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM emails WHERE user_email = %s", (user_email,))
        conn.commit()
        print(f"🗑️  Cleared emails for {user_email}")
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════
#  4. STATS FUNCTION (for dashboard counters)
# ══════════════════════════════════════════════════

def get_stats_for_user(user_email: str):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                COUNT(*)                                              AS total,
                SUM(CASE WHEN is_read = FALSE THEN 1 ELSE 0 END)      AS unread,
                SUM(CASE WHEN is_read = TRUE  THEN 1 ELSE 0 END)      AS read,
                SUM(CASE WHEN priority = 'high'   THEN 1 ELSE 0 END)  AS high,
                SUM(CASE WHEN priority = 'medium' THEN 1 ELSE 0 END)  AS medium,
                SUM(CASE WHEN priority = 'low'    THEN 1 ELSE 0 END)  AS low,
                SUM(CASE WHEN category = 'Work'        THEN 1 ELSE 0 END) AS work,
                SUM(CASE WHEN category = 'Finance'     THEN 1 ELSE 0 END) AS finance,
                SUM(CASE WHEN category = 'Promotions'  THEN 1 ELSE 0 END) AS promotions,
                SUM(CASE WHEN category = 'Social'      THEN 1 ELSE 0 END) AS social,
                SUM(CASE WHEN category = 'Newsletters' THEN 1 ELSE 0 END) AS newsletters,
                SUM(CASE WHEN category = 'Other'       THEN 1 ELSE 0 END) AS other
            FROM emails
            WHERE user_email = %s
        """, (user_email,))
        row = cursor.fetchone()
        conn.commit()

        empty = {"total":0,"unread":0,"read":0,"high":0,"medium":0,"low":0,
                 "work":0,"finance":0,"promotions":0,"social":0,"newsletters":0,"other":0}

        if not row or not row["total"]:
            return empty

        return {k: (row[k] or 0) for k in empty}
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════
#  SEARCH FUNCTION
# ══════════════════════════════════════════════════
def search_emails(user_email: str, query: str):
    if not query or not query.strip():
        return get_emails_for_user(user_email)

    conn = get_db()
    cursor = conn.cursor()
    try:
        q = f"%{query.strip()}%"
        cursor.execute("""
            SELECT * FROM emails
            WHERE user_email = %s
            AND (
                subject      ILIKE %s OR
                sender       ILIKE %s OR
                sender_email ILIKE %s OR
                snippet      ILIKE %s OR
                ai_summary   ILIKE %s
            )
            ORDER BY date DESC
            LIMIT 50
        """, (user_email, q, q, q, q, q))
        rows = cursor.fetchall()
        conn.commit()
        return [dict(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════
#  QUICK TEST — run this file directly to verify DB
# ══════════════════════════════════════════════════
if __name__ == "__main__":
    print("🔧 Testing database setup...")
    init_db()

    create_or_update_user(
        email="test@gmail.com",
        name="Test User",
        picture="https://example.com/pic.jpg",
        access_token="dummy_token_123"
    )

    user = get_user_by_email("test@gmail.com")
    print(f"✅ User found: {user['name']} ({user['email']})")

    save_email({
        "gmail_id":     "test_gmail_id_001",
        "user_email":   "test@gmail.com",
        "subject":      "Test Email Subject",
        "sender":       "Boss <boss@company.com>",
        "sender_email": "boss@company.com",
        "snippet":      "This is a test email snippet...",
        "body":         "This is the full body of the test email.",
        "date":         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "priority":     "high",
        "category":     "Work",
        "ai_summary":   "A test email to verify the database works."
    })

    stats = get_stats_for_user("test@gmail.com")
    print(f"✅ Stats: {stats}")

    print("\n🎉 database.py is working perfectly with PostgreSQL!")