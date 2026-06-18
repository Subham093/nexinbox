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
# ============================================================

import os
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

load_dotenv()

# ── Your Google credentials from .env ──────────────────────
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# ── This MUST match exactly what you put in Google Console ─
REDIRECT_URI = "http://localhost:8000/auth/callback"

# ── Google's OAuth endpoints (don't change these) ──────────
GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_URL  = "https://www.googleapis.com/oauth2/v2/userinfo"

# ── The "scopes" = what permissions we're asking for ───────
# openid        → confirm identity
# email         → see their email address
# profile       → see their name and picture
# gmail.readonly → READ their Gmail emails (not send/delete)
SCOPES = " ".join([
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
])

# ── Create the router (main.py imports this) ───────────────
router = APIRouter()


# ══════════════════════════════════════════════════
#  ROUTE 1: /auth/login
#  User clicks "Login with Google" → we send them to Google
# ══════════════════════════════════════════════════
@router.get("/login")
async def login(request: Request):
    """
    Builds the Google login URL and redirects the user there.
    
    The URL looks like:
    https://accounts.google.com/o/oauth2/v2/auth
        ?client_id=YOUR_ID
        &redirect_uri=http://localhost:8000/auth/callback
        &response_type=code
        &scope=openid email profile gmail.readonly
        &access_type=offline       ← gives us a refresh token
        &prompt=consent            ← always show consent screen
    """
    # Build the Google authorization URL with all required params
    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  REDIRECT_URI,
        "response_type": "code",         # We want an auth "code" back
        "scope":         SCOPES,
        "access_type":   "offline",      # Get refresh token too
        "prompt":        "consent",      # Always show consent (gets refresh token)
    }

    # Build URL query string manually
    from urllib.parse import urlencode
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    print(f"🔐 Redirecting to Google login...")
    return RedirectResponse(url=auth_url)


# ══════════════════════════════════════════════════
#  ROUTE 2: /auth/callback
#  Google sends user back here after they log in
# ══════════════════════════════════════════════════
@router.get("/callback")
async def auth_callback(request: Request, code: str = None, error: str = None):
    """
    Google redirects here after user approves/denies login.
    
    If approved → 'code' parameter is in the URL
    If denied   → 'error' parameter is in the URL
    
    Example URL Google sends:
    http://localhost:8000/auth/callback?code=4/0AX4XfWh...
    """

    # ── Did user deny access? ───────────────────────────────
    if error:
        print(f"❌ Google login denied: {error}")
        return RedirectResponse(url="/?error=login_denied")

    if not code:
        print("❌ No code received from Google")
        return RedirectResponse(url="/?error=no_code")

    # ── Step 1: Exchange the 'code' for real tokens ─────────
    # The 'code' is a one-time-use key. We swap it for:
    #   access_token  → lets us call Gmail API RIGHT NOW
    #   refresh_token → lets us get a new access_token when it expires
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id":     GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code":          code,
                    "redirect_uri":  REDIRECT_URI,
                    "grant_type":    "authorization_code",  # Always this value
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

        token_data = token_response.json()

        # Check if token exchange failed
        if "error" in token_data:
            print(f"❌ Token exchange failed: {token_data}")
            return RedirectResponse(url="/?error=token_failed")

        access_token  = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")  # May be None on re-login

        print(f"✅ Got access token from Google")

    except Exception as e:
        print(f"❌ Token exchange error: {e}")
        return RedirectResponse(url="/?error=token_error")

    # ── Step 2: Use access_token to get user's profile ──────
    # Call Google's userinfo API with the token as authorization
    try:
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                GOOGLE_USER_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )

        user_info = user_response.json()

        # user_info looks like:
        # {
        #   "id": "12345678",
        #   "email": "user@gmail.com",
        #   "name": "John Doe",
        #   "picture": "https://lh3.googleusercontent.com/..."
        # }

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

    # ── Step 3: Save user to database ───────────────────────
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

    # ── Step 4: Save to session ─────────────────────────────
    # The session is like a "memory" for this user's browser.
    # Whatever we store here is available in ALL other routes
    # via request.session.get("user_email") etc.
    request.session["user_email"]   = user_email
    request.session["user_name"]    = user_name
    request.session["user_picture"] = user_picture
    request.session["access_token"] = access_token

    print(f"✅ Session created for {user_email} — redirecting to dashboard")

    # ── Step 5: Send them to the dashboard! ─────────────────
    return RedirectResponse(url="/dashboard", status_code=302)


# ══════════════════════════════════════════════════
#  HELPER: Refresh expired access token
# ══════════════════════════════════════════════════
async def refresh_access_token(refresh_token: str, user_email: str):
    """
    Access tokens expire after ~1 hour.
    This function uses the refresh_token to get a new one silently
    (user doesn't need to log in again).
    
    Called from gmail.py if a token error occurs.
    """
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
            # Save new token to DB
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