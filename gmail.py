# ============================================================
#  gmail.py — Fetch Real Emails from Gmail API
# ============================================================

import httpx
import base64
import re
import html as html_module
from datetime import datetime
from fastapi import APIRouter

router = APIRouter()
GMAIL_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"


async def fetch_and_store_emails(user_email: str, access_token: str,
                                  mode: str = "full", latest_date: str = ""):
    """
    mode="full"    → fetch top 30 emails (first time)
    mode="refresh" → fetch latest 30, only SAVE the new ones not already in DB
    Existing emails in DB are NEVER deleted automatically.
    """
    print(f"\n📬 {'Full fetch' if mode == 'full' else 'Refresh fetch'} for {user_email}")
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        # ── Get message list ──────────────────────────────────
        async with httpx.AsyncClient(timeout=30) as client:
            list_response = await client.get(
                f"{GMAIL_BASE}/messages",
                headers=headers,
                params={"maxResults": 30, "labelIds": "INBOX"}  # ← 30 emails
            )

        if list_response.status_code == 401:
            print("❌ Token expired")
            return {"count": 0, "new": 0, "error": "token_expired"}

        if list_response.status_code != 200:
            print(f"❌ Gmail API error: {list_response.status_code}")
            return {"count": 0, "new": 0, "error": "api_error"}

        messages_list = list_response.json().get("messages", [])
        print(f"📋 Gmail returned {len(messages_list)} messages")

        if not messages_list:
            return {"count": 0, "new": 0}

        # ── Get existing gmail IDs from DB (to skip duplicates) ──
        existing_ids = set()
        try:
            from database import get_emails_for_user
            existing = get_emails_for_user(user_email, limit=200)
            existing_ids = {e["gmail_id"] for e in existing}
        except Exception:
            pass

        # ── Fetch + parse each message ────────────────────────
        emails_to_save = []
        skipped = 0

        async with httpx.AsyncClient(timeout=30) as client:
            for i, msg_ref in enumerate(messages_list):
                msg_id = msg_ref["id"]

                # Skip if already in database
                if msg_id in existing_ids:
                    skipped += 1
                    continue

                try:
                    msg_response = await client.get(
                        f"{GMAIL_BASE}/messages/{msg_id}",
                        headers=headers,
                        params={"format": "full"}
                    )
                    if msg_response.status_code != 200:
                        continue
                    parsed = parse_gmail_message(msg_response.json(), user_email)
                    if parsed:
                        emails_to_save.append(parsed)
                        print(f"  ✅ [{len(emails_to_save)}] New: {parsed['subject'][:50]}")
                except Exception as e:
                    print(f"  ⚠️  Error: {e}")
                    continue

        if skipped > 0:
            print(f"  ⏭️  Skipped {skipped} emails already in database")

        if not emails_to_save:
            print("✅ No new emails — inbox is up to date!")
            return {"count": len(existing_ids), "new": 0}

        # ── AI Analysis on NEW emails only ────────────────────
        print(f"\n🤖 AI analyzing {len(emails_to_save)} new emails...")
        try:
            from ai import analyze_emails_batch
            emails_to_save = await analyze_emails_batch(emails_to_save)
        except Exception as e:
            print(f"⚠️  AI failed, using defaults: {e}")
            for email in emails_to_save:
                if not email.get("priority"):   email["priority"]   = "medium"
                if not email.get("category"):   email["category"]   = "Other"
                if not email.get("ai_summary"): email["ai_summary"] = email.get("snippet", "")

        # ── Save new emails to DB ─────────────────────────────
        from database import save_emails_bulk
        save_emails_bulk(emails_to_save)

        print(f"✅ Done! Added {len(emails_to_save)} new emails for {user_email}")
        return {"count": len(existing_ids) + len(emails_to_save), "new": len(emails_to_save)}

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback; traceback.print_exc()
        return {"count": 0, "new": 0, "error": str(e)}


def parse_gmail_message(msg_data: dict, user_email: str) -> dict:
    try:
        gmail_id   = msg_data.get("id", "")
        snippet    = clean_snippet(msg_data.get("snippet", ""))
        payload    = msg_data.get("payload", {})
        headers    = payload.get("headers", [])
        header_map = {h["name"].lower(): h["value"] for h in headers}

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
            "is_read":      0,
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
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formats = [
        "%a, %d %b %Y %H:%M:%S %z", "%d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z", "%d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S",    "%d %b %Y %H:%M:%S",
    ]
    date_str = re.sub(r'\s*\([^)]*\)', '', date_str).strip()
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")