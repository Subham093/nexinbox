# ============================================================
#  auth.py — Google Login ("Who are you?")
# ============================================================
# This file handles the entire Google OAuth 2.0 login flow.
#
# The flow works like this:
#   1. User clicks "Login with Google" on your site
#   2. Your app redirects them to Google's login page
#   3. User logs in on Google and clicks "Allow"
#   4. Google redirects back to YOUR app with a "code"
#   5. Your app exchanges that code for real tokens
#   6. You use the token to get the user's name/email/picture
#   7. Save user to DB, store in session → logged in! ✅
#
# Routes in this file (all prefixed with /auth in main.py):
#   GET /auth/login     → Step 2: redirect to Google
#   GET /auth/callback  → Steps 4-7: handle Google's response

import os
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
    Redirects user to Google login page.
    Forces fresh consent screen every time so Gmail scope is always granted.
    """
    from urllib.parse import urlencode

    params = {
        "client_id":              GOOGLE_CLIENT_ID,
        "redirect_uri":           REDIRECT_URI,
        "response_type":          "code",
        "scope":                  SCOPES,
        "access_type":            "offline",
        "prompt":                 "consent select_account",  # Forces fresh consent
        "include_granted_scopes": "false",                   # Don't reuse old scopes
    }

    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    print(f"🔐 Redirecting to Google login...")
    print(f"🔍 Scopes requested: {SCOPES}")
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def auth_callback(request: Request, code: str = None, error: str = None):
    """
    Google redirects here after user approves login.
    Exchanges code for tokens, gets user profile, saves to DB and session.
    """

    if error:
        print(f"❌ Google login denied: {error}")
        return RedirectResponse(url="/?error=login_denied")

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

        # ── Debug: print what scopes were actually granted ──
        granted_scope = token_data.get("scope", "")
        print(f"✅ Token received!")
        print(f"🔍 Scopes granted: {granted_scope}")

        if "gmail" not in granted_scope:
            print("⚠️  WARNING: Gmail scope NOT granted!")
            print("   User needs to re-login and approve Gmail access")

        if "error" in token_data:
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

    # ── Save user to database ───────────────────────────────
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
        print(f"⚠️  DB save error (non-fatal): {e}")

    # ── Save to session ─────────────────────────────────────
    request.session["user_email"]   = user_email
    request.session["user_name"]    = user_name
    request.session["user_picture"] = user_picture
    request.session["access_token"] = access_token

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