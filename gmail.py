# ============================================================
#  gmail.py — Fetch Real Emails from Gmail API
#  CORRECTED VERSION — see CODE_REVIEW_REPORT.md for the diff
#  summary of every change made in this file.
# ============================================================

import asyncio
import httpx
import base64
import re
import html as html_module
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter

router = APIRouter()
GMAIL_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"

# NexInbox is a single-user portfolio project with no per-account timezone
# setting, unlike Gmail's own web UI (which converts every email's Date
# header to whatever timezone the Google account itself is configured
# with). To match that behavior, dates are converted to IST (UTC+5:30)
# here — a fixed offset, so no DST handling is needed for India. If this
# app is ever used from outside IST, this would need to become a real
# per-user setting instead of a hardcoded constant.
IST = timezone(timedelta(hours=5, minutes=30))


async def fetch_and_analyze_emails(user_email: str, access_token: str, skip_existing: bool = True):
    """
    Fetches the latest 30 inbox emails from Gmail, parses them, and runs
    AI analysis on them. Does NOT touch the database — the caller decides
    what to do with the results.

    skip_existing=True  → won't re-fetch/re-analyze emails whose gmail_id
                           is already stored for this user (cheap "just get
                           what's new" refresh). Used by fetch_and_store_emails.
    skip_existing=False → analyzes every email Gmail returns, even ones
                           already stored. Used for a true "start fresh"
                           re-sync (see /refresh-emails in main.py).

    Returns:
      {"emails": [...], "error": None}          on success
      {"emails": [], "error": "token_expired"}  if the access token is dead
      {"emails": [], "error": "<message>"}      on any other failure
    """
    print(f"\n📬 Fetching emails for {user_email} (skip_existing={skip_existing})")
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        # ── Get message list ──────────────────────────────────
        list_response = await _get_with_retry(
            f"{GMAIL_BASE}/messages", headers,
            params={"maxResults": 30, "labelIds": "INBOX"}
        )

        if list_response is None:
            return {"emails": [], "error": "rate_limited"}

        if list_response.status_code == 401:
            print("❌ Token expired")
            return {"emails": [], "error": "token_expired"}

        if list_response.status_code != 200:
            print(f"❌ Gmail API error: {list_response.status_code}")
            return {"emails": [], "error": "api_error"}

        messages_list = list_response.json().get("messages", [])
        print(f"📋 Gmail returned {len(messages_list)} messages")

        if not messages_list:
            return {"emails": [], "error": None}

        # ── Get existing gmail IDs from DB (to skip duplicates) ──
        # Uses a dedicated id-only query instead of get_emails_for_user's
        # `limit=200` — a user with more than 200 stored emails could
        # otherwise have old-but-still-inboxed mail silently re-analyzed
        # on every "check new emails" click.
        existing_ids = set()
        if skip_existing:
            try:
                from database import get_existing_gmail_ids
                existing_ids = get_existing_gmail_ids(user_email)
            except Exception as e:
                print(f"  ⚠️  Could not load existing IDs, will re-check every email: {e}")

        # ── Fetch + parse each message ────────────────────────
        emails_to_process = []
        skipped = 0

        async with httpx.AsyncClient(timeout=30) as client:
            for msg_ref in messages_list:
                msg_id = msg_ref["id"]

                if skip_existing and msg_id in existing_ids:
                    skipped += 1
                    continue

                try:
                    msg_response = await client.get(
                        f"{GMAIL_BASE}/messages/{msg_id}",
                        headers=headers,
                        params={"format": "full"}
                    )
                    if msg_response.status_code == 429:
                        print("  ⏳ Gmail rate limit hit mid-batch, backing off 2s")
                        await asyncio.sleep(2)
                        msg_response = await client.get(
                            f"{GMAIL_BASE}/messages/{msg_id}",
                            headers=headers, params={"format": "full"}
                        )
                    if msg_response.status_code != 200:
                        continue
                    parsed = parse_gmail_message(msg_response.json(), user_email)
                    if parsed:
                        emails_to_process.append(parsed)
                        print(f"  ✅ [{len(emails_to_process)}] {parsed['subject'][:50]}")
                except Exception as e:
                    print(f"  ⚠️  Error: {e}")
                    continue

        if skipped > 0:
            print(f"  ⏭️  Skipped {skipped} emails already in database")

        if not emails_to_process:
            print("✅ Nothing new to analyze")
            return {"emails": [], "error": None}

        # ── AI Analysis ────────────────────────────────────────
        print(f"\n🤖 AI analyzing {len(emails_to_process)} emails...")
        try:
            from ai import analyze_emails_batch
            emails_to_process = await analyze_emails_batch(emails_to_process)
        except Exception as e:
            print(f"⚠️  AI failed, using defaults: {e}")
            from ai import assign_defaults
            emails_to_process = assign_defaults(emails_to_process)

        return {"emails": emails_to_process, "error": None}

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback; traceback.print_exc()
        return {"emails": [], "error": str(e)}


async def _get_with_retry(url: str, headers: dict, params: dict, retries: int = 1):
    """Small helper: retry once after a short backoff on HTTP 429."""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers=headers, params=params)
        attempt = 0
        while response.status_code == 429 and attempt < retries:
            print("  ⏳ Gmail rate limit hit, backing off 2s")
            await asyncio.sleep(2)
            response = await client.get(url, headers=headers, params=params)
            attempt += 1
        return response


async def fetch_and_store_emails(user_email: str, access_token: str):
    """
    The normal "check my inbox" flow used by POST /fetch-emails.
    Fetches only NEW emails (ones not already saved), analyzes them,
    and saves them. Safe to call repeatedly — never creates duplicates,
    never deletes anything you already have.
    """
    result = await fetch_and_analyze_emails(user_email, access_token, skip_existing=True)

    if result["error"]:
        return {"count": 0, "new": 0, "error": result["error"]}

    new_emails = result["emails"]

    if new_emails:
        from database import save_emails_bulk
        save_emails_bulk(new_emails)
        print(f"✅ Done! Added {len(new_emails)} new emails for {user_email}")
    else:
        print("✅ No new emails — inbox is up to date!")

    try:
        from database import get_stats_for_user
        total = get_stats_for_user(user_email).get("total", 0)
    except Exception:
        total = len(new_emails)

    return {"count": total, "new": len(new_emails)}


def parse_gmail_message(msg_data: dict, user_email: str) -> dict:
    try:
        gmail_id   = msg_data.get("id", "")
        snippet    = clean_snippet(msg_data.get("snippet", ""))
        payload    = msg_data.get("payload", {})
        headers    = payload.get("headers", [])
        header_map = {h["name"].lower(): h["value"] for h in headers}

        # ── Real read/unread status from Gmail itself ──────────
        # Gmail tells us this directly: every message resource has a
        # top-level "labelIds" array. If "UNREAD" is in that list, the
        # message is unread in the user's real inbox; if it's absent,
        # the user has already read it there. Previously this was
        # hardcoded to False for every fetched email regardless of its
        # actual state in Gmail — that's what made the dashboard show
        # "30 unread" even when most of them were already read.
        label_ids = msg_data.get("labelIds", [])
        is_read   = "UNREAD" not in label_ids

        subject      = decode_mime_header(header_map.get("subject", "(No Subject)"))
        sender_raw   = header_map.get("from", "Unknown Sender")
        sender_name  = extract_sender_name(sender_raw)
        sender_email = extract_email_address(sender_raw)
        date         = parse_email_date(header_map.get("date", ""))
        body         = extract_body(payload)
        body         = clean_text(body) if body else snippet

        return {
            "gmail_id":     gmail_id,
            "user_email":   user_email,
            "subject":      subject[:500],
            "sender":       sender_name[:200],
            "sender_email": sender_email[:200],
            "snippet":      snippet[:300],
            "body":         body[:5000],
            "date":         date,
            "is_read":      is_read,   # matches the `emails.is_read BOOLEAN` column
            "priority":     "medium",
            "category":     "Other",
            "ai_summary":   "",
        }
    except Exception as e:
        print(f"  ⚠️  Parse error: {e}")
        return None


def extract_sender_name(sender: str) -> str:
    sender = html_module.unescape(sender)
    match  = re.match(r'^"?([^"<]+)"?\s*<[^>]+>$', sender.strip())
    if match:
        name = match.group(1).strip().strip('"')
        if name:
            return name
    email_match = re.search(r'<([^>]+)>', sender)
    if email_match:
        return email_match.group(1).strip()
    return sender.strip()


def extract_email_address(sender: str) -> str:
    sender = html_module.unescape(sender)
    match  = re.search(r'<([^>]+)>', sender)
    if match:
        return match.group(1).strip()
    if "@" in sender:
        return sender.strip()
    return sender.strip()


def decode_mime_header(value: str) -> str:
    try:
        from email.header import decode_header
        parts   = decode_header(value)
        decoded = ""
        for part, encoding in parts:
            if isinstance(part, bytes):
                decoded += part.decode(encoding or "utf-8", errors="replace")
            else:
                decoded += str(part)
        return decoded
    except Exception:
        return value


def clean_snippet(snippet: str) -> str:
    return html_module.unescape(snippet) if snippet else ""


def extract_body(payload: dict) -> str:
    mime_type = payload.get("mimeType", "")
    if "data" in payload.get("body", {}):
        body = decode_base64(payload["body"]["data"])
        return strip_html(body) if mime_type == "text/html" else body
    parts = payload.get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data: return decode_base64(data)
    for part in parts:
        if part.get("mimeType") == "text/html":
            data = part.get("body", {}).get("data", "")
            if data: return strip_html(decode_base64(data))
    for part in parts:
        if "multipart" in part.get("mimeType", ""):
            nested = extract_body(part)
            if nested: return nested
    return ""


def decode_base64(data: str) -> str:
    try:
        data    = data.replace("-", "+").replace("_", "/")
        padding = 4 - len(data) % 4
        if padding != 4: data += "=" * padding
        return base64.b64decode(data).decode("utf-8", errors="replace")
    except Exception:
        return ""


def strip_html(html: str) -> str:
    html = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '',
                  html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<[^>]+>', ' ', html)
    return html_module.unescape(html)


def clean_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return " ".join(lines[:100])


def parse_email_date(date_str: str) -> str:
    """
    Parses a raw Gmail "Date" header and returns it as a local (IST)
    timestamp string, matching what Gmail's own web UI shows.

    BUG FIX: the previous version parsed the timezone offset (%z) from
    the header correctly, but then formatted the datetime WITHOUT
    converting it — so an email timestamped in UTC (or any non-IST
    offset) displayed its raw original-timezone clock time and date
    instead of the local time a user would actually expect, sometimes
    shifting the date itself by a day. Now, whenever the header
    includes a parseable UTC offset, the datetime is explicitly
    converted to IST before formatting.
    """
    if not date_str:
        return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

    date_str = re.sub(r'\s*\([^)]*\)', '', date_str).strip()

    # Formats that include a numeric UTC offset (%z) — these can be
    # reliably converted to IST.
    offset_formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%d %b %Y %H:%M:%S %z",
    ]
    for fmt in offset_formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    # Formats with a named zone (%Z) or no zone at all — Python's %Z
    # parsing is unreliable for anything but UTC/local, so there's no
    # trustworthy offset to convert from here. Parsed and returned as-is
    # rather than guessing, which was also the previous behavior.
    naive_formats = [
        "%a, %d %b %Y %H:%M:%S %Z", "%d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S",    "%d %b %Y %H:%M:%S",
    ]
    for fmt in naive_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")