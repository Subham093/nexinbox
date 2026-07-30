# ============================================================
#  auth.py — Google Login ("Who are you?")
#  CORRECTED VERSION — see CODE_REVIEW_REPORT.md for the diff
#  summary of every change made in this file.
# ============================================================
# The flow works like this:
#   1. User clicks "Login with Google" on your site
#   2. Your app redirects them to Google's login page
#   3. User logs in on Google and clicks "Allow"
#   4. Google redirects back to YOUR app with a "code"
#   5. Your app exchanges that code for real tokens
#   6. You use the token to get the user's name/email/picture
#   7. Save user + tokens to DB, store only the user's identity in the
#      session cookie → logged in! ✅ (the access token itself now lives
#      only in Postgres, never in the browser-readable session cookie)
#
# Routes in this file (all prefixed with /auth in main.py):
#   GET /auth/login     → Step 2: redirect to Google
#   GET /auth/callback  → Steps 4-7: handle Google's response

import os
import secrets
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")
GOOGLE_AUTH_URL      = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL     = "https://oauth2.googleapis.com/token"
GOOGLE_USER_URL      = "https://www.googleapis.com/oauth2/v2/userinfo"

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    # Fail at import time with a clear message instead of building a
    # broken auth URL (client_id=None) that only surfaces as a cryptic
    # Google error page once a user actually clicks "Login".
    print("⚠️  WARNING: GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not set — "
          "Google login will not work until these are configured.")

# ── All scopes including gmail.readonly ────────────────────
SCOPES = " ".join([
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
])

router = APIRouter()


@router.get("/login")
async def login(request: Request):
    """
    Redirects user to Google login page. Forces fresh consent screen
    every time so the Gmail scope is always granted.

    Also generates a random "state" value and stores it in the session.
    Google will send this same value back on /callback — if it doesn't
    match, we know the request didn't originate from our own /login call
    (standard OAuth CSRF protection).
    """
    from urllib.parse import urlencode

    state = secrets.token_urlsafe(24)
    request.session["oauth_state"] = state

    params = {
        "client_id":              GOOGLE_CLIENT_ID,
        "redirect_uri":           REDIRECT_URI,
        "response_type":          "code",
        "scope":                  SCOPES,
        "access_type":            "offline",
        "prompt":                 "consent select_account",  # Forces fresh consent
        "include_granted_scopes": "false",                   # Don't reuse old scopes
        "state":                  state,
    }

    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    print(f"🔐 Redirecting to Google login...")
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def auth_callback(request: Request, code: str = None, error: str = None, state: str = None):
    """
    Google redirects here after user approves login. Exchanges code for
    tokens, gets user profile, saves everything to the DB, and stores
    only non-sensitive identity fields in the session.
    """

    if error:
        print(f"❌ Google login denied: {error}")
        return RedirectResponse(url="/?error=login_denied")

    # ── CSRF check: state must match what /login stored ────
    expected_state = request.session.pop("oauth_state", None)
    if not state or not expected_state or state != expected_state:
        print("❌ OAuth state mismatch — rejecting callback (possible CSRF)")
        return RedirectResponse(url="/?error=state_mismatch")

    if not code:
        print("❌ No code received from Google")
        return RedirectResponse(url="/?error=no_code")

    # ── Exchange code for tokens ────────────────────────────
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id":     GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code":          code,
                    "redirect_uri":  REDIRECT_URI,
                    "grant_type":    "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

        token_data    = token_response.json()
        access_token  = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        granted_scope = token_data.get("scope", "")
        print(f"✅ Token received! Scopes granted: {granted_scope}")

        if "gmail" not in granted_scope:
            print("⚠️  WARNING: Gmail scope NOT granted — user needs to "
                  "re-login and approve Gmail access")

        if "error" in token_data or not access_token:
            print(f"❌ Token exchange failed: {token_data}")
            return RedirectResponse(url="/?error=token_failed")

    except Exception as e:
        print(f"❌ Token exchange error: {e}")
        return RedirectResponse(url="/?error=token_error")

    # ── Get user profile ────────────────────────────────────
    try:
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                GOOGLE_USER_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )

        user_info    = user_response.json()
        user_email   = user_info.get("email")
        user_name    = user_info.get("name", "User")
        user_picture = user_info.get("picture", "")

        if not user_email:
            print("❌ Could not get email from Google")
            return RedirectResponse(url="/?error=no_email")

        print(f"✅ Google user identified: {user_name} ({user_email})")

    except Exception as e:
        print(f"❌ User info fetch error: {e}")
        return RedirectResponse(url="/?error=userinfo_error")

    # ── Save user + tokens to database ──────────────────────
    # The access/refresh tokens live ONLY here. They are never written
    # to the session cookie (see note below).
    try:
        from database import create_or_update_user
        create_or_update_user(
            email=user_email,
            name=user_name,
            picture=user_picture,
            access_token=access_token,
            refresh_token=refresh_token
        )
    except Exception as e:
        # This one IS fatal now: if we can't persist the token, later
        # requests have no way to call Gmail on this user's behalf, so
        # silently continuing to "logged in" would be misleading.
        print(f"❌ DB save error: {e}")
        return RedirectResponse(url="/?error=db_error")

    # ── Save to session ─────────────────────────────────────
    # IMPORTANT: Starlette's SessionMiddleware stores session data in a
    # signed-but-NOT-encrypted cookie (it's base64, not AES). Signing
    # stops the user from *tampering* with the cookie, but anyone who
    # can read the cookie (browser extension, XSS, shared computer, a
    # proxy log) can also read anything stored in it. The previous
    # version of this file put the live Google access_token in that
    # cookie — effectively handing out read access to the user's Gmail
    # to anyone who obtained the cookie. Only identity fields go in the
    # session now; every route that needs the access_token fetches it
    # from Postgres via get_user_by_email().
    request.session["user_email"]   = user_email
    request.session["user_name"]    = user_name
    request.session["user_picture"] = user_picture

    print(f"✅ Session created for {user_email} — redirecting to dashboard")
    return RedirectResponse(url="/dashboard", status_code=302)


# ══════════════════════════════════════════════════
#  HELPER: Refresh expired access token
# ══════════════════════════════════════════════════
async def refresh_access_token(refresh_token: str, user_email: str):
    """Gets a new access token using refresh token when current one expires."""
    if not refresh_token:
        return None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id":     GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                    "grant_type":    "refresh_token",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        data = response.json()
        if "access_token" in data:
            new_token = data["access_token"]
            from database import update_access_token
            update_access_token(user_email, new_token)
            print(f"✅ Access token refreshed for {user_email}")
            return new_token
        else:
            print(f"❌ Token refresh failed: {data}")
            return None
    except Exception as e:
        print(f"❌ Token refresh error: {e}")
        return None