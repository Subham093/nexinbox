# ============================================================
#  database.py — Your Storage Room (Now backed by PostgreSQL!)
# ============================================================
# We migrated from SQLite (a file that lived INSIDE the app,
# and got wiped every time Render restarted) to PostgreSQL
# (a separate, permanent database hosted on Supabase).
#
# This file still does the same 4 things as before:
#   1. Creates the database + tables (init_db)
#   2. User functions   (create/get users)
#   3. Email functions  (save/get/filter emails)
#   4. Stats function   (count totals for dashboard)
# ============================================================

import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Where the database actually lives now ──────────────────
# Instead of a local file, this is a URL pointing to your
# Supabase Postgres database (kept secret in your .env file)
DATABASE_URL = os.getenv("DATABASE_URL")


# ══════════════════════════════════════════════════
#  HELPER: Get a database connection
# ══════════════════════════════════════════════════
def get_db():
    """
    Opens a connection to the PostgreSQL database.

    cursor_factory=RealDictCursor means:
      Instead of getting back plain tuples like ("abc@gmail.com", "John"),
      you get dict-like objects: row["email"], row["name"]  ← same as before!
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


# ══════════════════════════════════════════════════
#  1. INIT: Create all tables if they don't exist
# ══════════════════════════════════════════════════
def init_db():
    """
    Called once on server startup (from main.py).
    Creates 2 tables:
      - users  → stores Google login info
      - emails → stores fetched + AI-analyzed emails

    "IF NOT EXISTS" = safe to call multiple times, won't wipe data!
    """
    conn = get_db()
    cursor = conn.cursor()

    # ── TABLE 1: users ──────────────────────────────────────
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

    # ── TABLE 2: emails ─────────────────────────────────────
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
            date          TEXT,
            is_read       INTEGER DEFAULT 0,
            priority      TEXT    DEFAULT 'medium',
            category      TEXT    DEFAULT 'Other',
            ai_summary    TEXT,
            fetched_at    TIMESTAMP DEFAULT NOW(),

            UNIQUE(gmail_id, user_email)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Database ready (PostgreSQL / Supabase)")


# ══════════════════════════════════════════════════
#  2. USER FUNCTIONS
# ══════════════════════════════════════════════════

def create_or_update_user(email: str, name: str, picture: str,
                           access_token: str, refresh_token: str = None):
    """
    Called after Google login succeeds.
    - If user exists → updates their tokens + last_login
    - If new user    → creates a fresh row
    """
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
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email: str):
    """
    Looks up a user by their email address.
    Returns a dict-like Row object, or None if not found.
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        cursor.close()
        conn.close()


def update_access_token(email: str, access_token: str):
    """Updates just the access token (used when token refreshes)."""
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
    """
    Saves one email to the database.
    "ON CONFLICT DO NOTHING" = if this email already exists, skip it silently.
    This prevents duplicates when you fetch emails multiple times.
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO emails
                (gmail_id, user_email, subject, sender, sender_email,
                 snippet, body, date, priority, category, ai_summary)
            VALUES
                (%(gmail_id)s, %(user_email)s, %(subject)s, %(sender)s, %(sender_email)s,
                 %(snippet)s, %(body)s, %(date)s, %(priority)s, %(category)s, %(ai_summary)s)
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
    """
    Saves multiple emails at once — much faster than calling save_email() in a loop!
    Used after fetching all new emails from Gmail + running AI on them.
    """
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
                         snippet, body, date, priority, category, ai_summary)
                    VALUES
                        (%(gmail_id)s, %(user_email)s, %(subject)s, %(sender)s, %(sender_email)s,
                         %(snippet)s, %(body)s, %(date)s, %(priority)s, %(category)s, %(ai_summary)s)
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


def get_emails_for_user(user_email: str, limit: int = 50):
    """
    Gets all emails for a user, newest first.
    Returns a list of dicts (easy to use in templates).
    """
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
        return [dict(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


def get_email_by_id(gmail_id: str, user_email: str):
    """
    Gets one specific email by its Gmail ID.
    Also checks user_email so users can't see each other's emails!
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM emails
            WHERE gmail_id = %s AND user_email = %s
        """, (gmail_id, user_email))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        cursor.close()
        conn.close()


def mark_email_as_read(gmail_id: str, user_email: str = None):
    """
    Sets is_read = 1 for an email (called when user opens it).
    Now also scoped by user_email when provided, for safety.
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        if user_email:
            cursor.execute(
                "UPDATE emails SET is_read = 1 WHERE gmail_id = %s AND user_email = %s",
                (gmail_id, user_email)
            )
        else:
            cursor.execute(
                "UPDATE emails SET is_read = 1 WHERE gmail_id = %s",
                (gmail_id,)
            )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_filtered_emails(user_email: str, priority: str = None,
                         category: str = None, read_status: str = None):
    """
    Gets emails with optional filters.
    Any filter left as None is ignored (shows everything).
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        query  = "SELECT * FROM emails WHERE user_email = %s"
        params = [user_email]

        if priority:
            query += " AND priority = %s"
            params.append(priority.lower())

        if category:
            query += " AND category = %s"
            params.append(category)

        if read_status == "unread":
            query += " AND is_read = 0"
        elif read_status == "read":
            query += " AND is_read = 1"

        query += " ORDER BY date DESC LIMIT 50"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


def delete_emails_for_user(user_email: str):
    """
    Deletes all emails for a user (used when they want to re-fetch fresh emails).
    """
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
    """
    Returns counts for the dashboard stat cards.
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                COUNT(*)                                         AS total,
                SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END)   AS unread,
                SUM(CASE WHEN is_read = 1 THEN 1 ELSE 0 END)   AS read,
                SUM(CASE WHEN priority = 'high'   THEN 1 ELSE 0 END) AS high,
                SUM(CASE WHEN priority = 'medium' THEN 1 ELSE 0 END) AS medium,
                SUM(CASE WHEN priority = 'low'    THEN 1 ELSE 0 END) AS low,
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

        if row and row["total"]:
            return {
                "total":       row["total"]       or 0,
                "unread":      row["unread"]      or 0,
                "read":        row["read"]        or 0,
                "high":        row["high"]        or 0,
                "medium":      row["medium"]      or 0,
                "low":         row["low"]         or 0,
                "work":        row["work"]        or 0,
                "finance":     row["finance"]     or 0,
                "promotions":  row["promotions"]  or 0,
                "social":      row["social"]      or 0,
                "newsletters": row["newsletters"] or 0,
                "other":       row["other"]       or 0,
            }
        # Return zeroes if no emails yet
        return {"total":0,"unread":0,"read":0,"high":0,"medium":0,"low":0,
                "work":0,"finance":0,"promotions":0,"social":0,"newsletters":0,"other":0}
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════
#  SEARCH FUNCTION
# ══════════════════════════════════════════════════
def search_emails(user_email: str, query: str):
    """
    Search emails by subject, sender, or body content.
    Case-insensitive search using SQL LIKE.
    """
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
        return [dict(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


# ══════════════════════════════════════════════════
#  QUICK TEST — run this file directly to verify DB
# ══════════════════════════════════════════════════
# Run:  python database.py
# You should see the success messages, and can check
# your Supabase dashboard's Table Editor to see the data!
if __name__ == "__main__":
    print("🔧 Testing database setup...")
    init_db()

    # Test: create a dummy user
    create_or_update_user(
        email="test@gmail.com",
        name="Test User",
        picture="https://example.com/pic.jpg",
        access_token="dummy_token_123"
    )

    # Test: fetch that user back
    user = get_user_by_email("test@gmail.com")
    print(f"✅ User found: {user['name']} ({user['email']})")

    # Test: save a dummy email
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

    # Test: get stats
    stats = get_stats_for_user("test@gmail.com")
    print(f"✅ Stats: {stats}")

    print("\n🎉 database.py is working perfectly with PostgreSQL!")