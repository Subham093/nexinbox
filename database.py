# ============================================================
#  database.py — Your Storage Room
# ============================================================
# SQLite is a simple file-based database — no installation needed!
# It creates a file called "email_intelligence.db" in your project.
# 
# This file does 4 things:
#   1. Creates the database + tables (init_db)
#   2. User functions   (create/get users)
#   3. Email functions  (save/get/filter emails)
#   4. Stats function   (count totals for dashboard)
# ============================================================

import sqlite3
import os
from datetime import datetime

# ── Where the database file will be saved ──────────────────
# This creates "email_intelligence.db" right inside your project folder
DB_PATH = os.path.join(os.path.dirname(__file__), "email_intelligence.db")


# ══════════════════════════════════════════════════
#  HELPER: Get a database connection
# ══════════════════════════════════════════════════
def get_db():
    """
    Opens a connection to the SQLite database.
    
    row_factory = sqlite3.Row means:
      Instead of getting back plain tuples like ("abc@gmail.com", "John"),
      you get dict-like objects: row["email"], row["name"]  ← much nicer!
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name, not index
    conn.execute("PRAGMA journal_mode=WAL")   # Better performance
    conn.execute("PRAGMA foreign_keys=ON")    # Enforce relationships
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
    # Stores everyone who logs in via Google OAuth
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT    UNIQUE NOT NULL,   -- Google email (unique per person)
            name          TEXT,                       -- Full name from Google
            picture       TEXT,                       -- Profile picture URL
            access_token  TEXT,                       -- Gmail API access token
            refresh_token TEXT,                       -- To refresh expired access tokens
            created_at    TEXT    DEFAULT (datetime('now')),
            last_login    TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── TABLE 2: emails ─────────────────────────────────────
    # Stores the fetched + AI-analyzed emails for each user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            gmail_id      TEXT    NOT NULL,           -- Gmail's own message ID
            user_email    TEXT    NOT NULL,           -- Which user this belongs to
            subject       TEXT    DEFAULT '(No Subject)',
            sender        TEXT,                       -- "John Doe <john@example.com>"
            sender_email  TEXT,                       -- Just "john@example.com"
            snippet       TEXT,                       -- Short preview (first ~100 chars)
            body          TEXT,                       -- Full email body text
            date          TEXT,                       -- When email was received
            is_read       INTEGER DEFAULT 0,          -- 0 = unread, 1 = read
            priority      TEXT    DEFAULT 'medium',   -- "high" | "medium" | "low"
            category      TEXT    DEFAULT 'Other',    -- "Work" | "Finance" | etc.
            ai_summary    TEXT,                       -- AI-generated summary
            fetched_at    TEXT    DEFAULT (datetime('now')),
            
            -- Prevent saving the same email twice for the same user
            UNIQUE(gmail_id, user_email)
        )
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database ready at: {DB_PATH}")


# ══════════════════════════════════════════════════
#  2. USER FUNCTIONS
# ══════════════════════════════════════════════════

def create_or_update_user(email: str, name: str, picture: str,
                           access_token: str, refresh_token: str = None):
    """
    Called after Google login succeeds.
    - If user exists → updates their tokens + last_login
    - If new user    → creates a fresh row
    
    "INSERT OR REPLACE" handles both cases in one SQL statement!
    """
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO users (email, name, picture, access_token, refresh_token, last_login)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(email) DO UPDATE SET
                name          = excluded.name,
                picture       = excluded.picture,
                access_token  = excluded.access_token,
                refresh_token = COALESCE(excluded.refresh_token, refresh_token),
                last_login    = datetime('now')
        """, (email, name, picture, access_token, refresh_token))
        conn.commit()
        print(f"✅ User saved: {email}")
    except Exception as e:
        print(f"❌ Error saving user: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_user_by_email(email: str):
    """
    Looks up a user by their email address.
    Returns a dict-like Row object, or None if not found.
    
    Usage:
        user = get_user_by_email("abc@gmail.com")
        print(user["name"])   # "John Doe"
    """
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_access_token(email: str, access_token: str):
    """Updates just the access token (used when token refreshes)."""
    conn = get_db()
    try:
        conn.execute(
            "UPDATE users SET access_token = ? WHERE email = ?",
            (access_token, email)
        )
        conn.commit()
    finally:
        conn.close()


# ══════════════════════════════════════════════════
#  3. EMAIL FUNCTIONS
# ══════════════════════════════════════════════════

def save_email(email_data: dict):
    """
    Saves one email to the database.
    
    email_data should be a dict like:
    {
        "gmail_id":     "18d4f2a3b9c1e5f7",
        "user_email":   "user@gmail.com",
        "subject":      "Meeting Tomorrow",
        "sender":       "Boss <boss@company.com>",
        "sender_email": "boss@company.com",
        "snippet":      "Hi, just a reminder...",
        "body":         "Hi, just a reminder about...",
        "date":         "2024-01-15 10:30:00",
        "priority":     "high",
        "category":     "Work",
        "ai_summary":   "Boss reminds about tomorrow's meeting at 10am."
    }
    
    "INSERT OR IGNORE" = if this email already exists, skip it silently.
    This prevents duplicates when you fetch emails multiple times.
    """
    conn = get_db()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO emails
                (gmail_id, user_email, subject, sender, sender_email,
                 snippet, body, date, priority, category, ai_summary)
            VALUES
                (:gmail_id, :user_email, :subject, :sender, :sender_email,
                 :snippet, :body, :date, :priority, :category, :ai_summary)
        """, email_data)
        conn.commit()
    except Exception as e:
        print(f"❌ Error saving email {email_data.get('gmail_id')}: {e}")
        conn.rollback()
    finally:
        conn.close()


def save_emails_bulk(emails_list: list):
    """
    Saves multiple emails at once — much faster than calling save_email() in a loop!
    Used after fetching all 50 emails from Gmail + running AI on them.
    """
    if not emails_list:
        return

    conn = get_db()
    saved_count = 0
    try:
        for email_data in emails_list:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO emails
                        (gmail_id, user_email, subject, sender, sender_email,
                         snippet, body, date, priority, category, ai_summary)
                    VALUES
                        (:gmail_id, :user_email, :subject, :sender, :sender_email,
                         :snippet, :body, :date, :priority, :category, :ai_summary)
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
        conn.close()


def get_emails_for_user(user_email: str, limit: int = 50):
    """
    Gets all emails for a user, newest first.
    Returns a list of dicts (easy to use in templates).
    
    Usage:
        emails = get_emails_for_user("user@gmail.com")
        for email in emails:
            print(email["subject"], email["priority"])
    """
    conn = get_db()
    try:
        rows = conn.execute("""
            SELECT * FROM emails
            WHERE user_email = ?
            ORDER BY date DESC, fetched_at DESC
            LIMIT ?
        """, (user_email, limit)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_email_by_id(gmail_id: str, user_email: str):
    """
    Gets one specific email by its Gmail ID.
    Also checks user_email so users can't see each other's emails!
    """
    conn = get_db()
    try:
        row = conn.execute("""
            SELECT * FROM emails
            WHERE gmail_id = ? AND user_email = ?
        """, (gmail_id, user_email)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def mark_email_as_read(gmail_id: str):
    """Sets is_read = 1 for an email (called when user opens it)."""
    conn = get_db()
    try:
        conn.execute(
            "UPDATE emails SET is_read = 1 WHERE gmail_id = ?",
            (gmail_id,)
        )
        conn.commit()
    finally:
        conn.close()


def get_filtered_emails(user_email: str, priority: str = None,
                         category: str = None, read_status: str = None):
    """
    Gets emails with optional filters.
    Any filter left as None is ignored (shows everything).
    
    Examples:
        get_filtered_emails("u@g.com", priority="high")
        get_filtered_emails("u@g.com", category="Work")
        get_filtered_emails("u@g.com", read_status="unread")
    """
    conn = get_db()
    try:
        # Build query dynamically based on which filters are active
        query  = "SELECT * FROM emails WHERE user_email = ?"
        params = [user_email]

        if priority:
            query += " AND priority = ?"
            params.append(priority.lower())

        if category:
            query += " AND category = ?"
            params.append(category)

        if read_status == "unread":
            query += " AND is_read = 0"
        elif read_status == "read":
            query += " AND is_read = 1"

        query += " ORDER BY date DESC LIMIT 50"

        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_emails_for_user(user_email: str):
    """
    Deletes all emails for a user (used when they want to re-fetch fresh emails).
    """
    conn = get_db()
    try:
        conn.execute("DELETE FROM emails WHERE user_email = ?", (user_email,))
        conn.commit()
        print(f"🗑️  Cleared emails for {user_email}")
    finally:
        conn.close()


# ══════════════════════════════════════════════════
#  4. STATS FUNCTION (for dashboard counters)
# ══════════════════════════════════════════════════

def get_stats_for_user(user_email: str):
    """
    Returns counts for the dashboard stat cards.
    
    Returns a dict like:
    {
        "total":  50,
        "unread": 12,
        "read":   38,
        "high":    8,
        "medium": 25,
        "low":    17,
        "work":   15,
        "finance": 5,
        ...
    }
    """
    conn = get_db()
    try:
        # One query to get all counts using conditional SUM
        # SUM(CASE WHEN condition THEN 1 ELSE 0 END) = count where condition is true
        row = conn.execute("""
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
            WHERE user_email = ?
        """, (user_email,)).fetchone()

        if row:
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
        conn.close()


# ══════════════════════════════════════════════════
#  QUICK TEST — run this file directly to verify DB
# ══════════════════════════════════════════════════
# Run:  python database.py
# You should see the success messages and a .db file created
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

    print("\n🎉 database.py is working perfectly!")
    print(f"📁 Database file created at: {DB_PATH}")


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
    try:
        q = f"%{query.strip()}%"
        rows = conn.execute("""
            SELECT * FROM emails
            WHERE user_email = ?
            AND (
                subject      LIKE ? OR
                sender       LIKE ? OR
                sender_email LIKE ? OR
                snippet      LIKE ? OR
                ai_summary   LIKE ?
            )
            ORDER BY date DESC
            LIMIT 50
        """, (user_email, q, q, q, q, q)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()