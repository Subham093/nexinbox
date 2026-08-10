#  main.py — Entry Point
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.concurrency import run_in_threadpool
from dotenv import load_dotenv

load_dotenv()

try:
    from database import (
        init_db, get_emails_for_user, get_stats_for_user, get_email_by_id,
        mark_email_as_read, get_filtered_emails, search_emails as db_search,
        get_user_by_email, replace_all_emails_for_user,
    )
except Exception as e:
    print(f"⚠️  Could not import database.py — real reason: {e}")
    init_db = None

try:
    from auth import router as auth_router, refresh_access_token
except Exception as e:
    print(f"⚠️  Could not import auth.py — real reason: {e}")
    auth_router = None

try:
    from gmail import router as gmail_router, fetch_and_store_emails, fetch_and_analyze_emails
except Exception as e:
    print(f"⚠️  Could not import gmail.py — real reason: {e}")
    gmail_router = None

# ══════════════════════════════════════════════════
app = FastAPI(title="NexInbox", version="1.0.0")

IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise RuntimeError(
            "SECRET_KEY must be set in production — refusing to start with a "
            "public, guessable key that lets anyone forge a login session."
        )
    print("⚠️  WARNING: SECRET_KEY is not set — falling back to an insecure "
          "default. This is only allowed because ENVIRONMENT is not 'production'.")
    SECRET_KEY = "change-this-in-production-please"

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=86400,
    https_only=IS_PRODUCTION,
    same_site="lax"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

if auth_router:
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
if gmail_router:
    app.include_router(gmail_router, prefix="/gmail", tags=["Gmail"])


def get_current_user(request: Request):
    return request.session.get("user_email")


async def get_access_token_for(user_email: str):
    """
    The access token lives only in Postgres (see auth.py). This is the
    single place every route goes through to get it.

    Now async + wrapped in try/except: psycopg2 is a blocking driver, so
    the DB call is pushed onto a background thread (run_in_threadpool)
    instead of freezing every other user's request while it runs. The
    try/except means a DB hiccup here produces a clean "please log in
    again" redirect instead of an unhandled 500.
    """
    if not user_email:
        return None
    try:
        user_row = await run_in_threadpool(get_user_by_email, user_email)
        return user_row.get("access_token") if user_row else None
    except Exception as e:
        print(f"⚠️  Could not fetch access token for {user_email}: {e}")
        return None


#  ROUTE 1: Home

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if get_current_user(request):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(request, "index.html",
        {"title": "NexInbox"})


#  ROUTE 2: Dashboard

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user_email = get_current_user(request)
    if not user_email:
        return RedirectResponse(url="/", status_code=302)

    user_name    = request.session.get("user_name", "User")
    user_picture = request.session.get("user_picture", "")
    emails = []
    stats  = _empty_stats()

    try:
        emails = await run_in_threadpool(get_emails_for_user, user_email)
        stats  = await run_in_threadpool(get_stats_for_user, user_email)
    except Exception as e:
        print(f"DB error: {e}")

    return templates.TemplateResponse(request, "dashboard.html", {
        "user_email":    user_email,
        "user_name":     user_name,
        "user_picture":  user_picture,
        "emails":        emails,
        "stats":         stats,
        "active_filter": "all",
        "title":         "Dashboard — Email Intelligence",
    })


#  ROUTE 3: Email Detail

@app.get("/email/{email_id}", response_class=HTMLResponse)
async def email_detail(request: Request, email_id: str):
    user_email = get_current_user(request)
    if not user_email:
        return RedirectResponse(url="/", status_code=302)

    email_data = None
    try:
        email_data = await run_in_threadpool(get_email_by_id, email_id, user_email)
        if email_data and not email_data.get("is_read"):
            await run_in_threadpool(mark_email_as_read, email_id, user_email)
            email_data["is_read"] = True
    except Exception as e:
        print(f"DB error: {e}")

    if not email_data:
        raise HTTPException(status_code=404, detail="Email not found")

    return templates.TemplateResponse(request, "email_detail.html", {
        "email":        email_data,
        "user_name":    request.session.get("user_name", "User"),
        "user_picture": request.session.get("user_picture", ""),
        "title":        f"Email — {email_data.get('subject', 'No Subject')}",
    })


#  ROUTE 4: Fetch Emails (SMART — only pulls what's new)

@app.post("/fetch-emails")
async def fetch_emails(request: Request):
    user_email = get_current_user(request)
    if not user_email:
        return RedirectResponse(url="/", status_code=302)

    access_token = await get_access_token_for(user_email)
    if not access_token:
        request.session.clear()
        return RedirectResponse(url="/auth/login", status_code=302)

    try:
        result = await fetch_and_store_emails(user_email=user_email, access_token=access_token)

        if result.get("error") == "token_expired":
            print("🔑 Access token expired — attempting silent refresh")
            user_row = await run_in_threadpool(get_user_by_email, user_email)
            refresh_token = user_row.get("refresh_token") if user_row else None
            new_token = await refresh_access_token(refresh_token, user_email) if refresh_token else None

            if new_token:
                result = await fetch_and_store_emails(user_email=user_email, access_token=new_token)

            if not new_token or result.get("error") == "token_expired":
                print("🔑 Refresh failed — user must log in again")
                return RedirectResponse(url="/auth/login", status_code=302)

        new_count = result.get("new", 0)
        print(f"✅ {new_count} new emails added" if new_count > 0 else "✅ Inbox up to date")

    except Exception as e:
        print(f"❌ Fetch error: {e}")
        import traceback; traceback.print_exc()

    return RedirectResponse(url="/dashboard", status_code=302)


#  ROUTE 5: Force Refresh (fetch fresh copy, THEN atomically replace)

@app.post("/refresh-emails")
async def refresh_emails(request: Request):
    user_email = get_current_user(request)
    if not user_email:
        return RedirectResponse(url="/", status_code=302)

    access_token = await get_access_token_for(user_email)
    if not access_token:
        request.session.clear()
        return RedirectResponse(url="/auth/login", status_code=302)

    try:
        print(f"🔄 Force refresh for {user_email}")
        result = await fetch_and_analyze_emails(user_email, access_token, skip_existing=False)

        if result["error"] == "token_expired":
            print("🔑 Access token expired — attempting silent refresh")
            user_row = await run_in_threadpool(get_user_by_email, user_email)
            refresh_token = user_row.get("refresh_token") if user_row else None
            new_token = await refresh_access_token(refresh_token, user_email) if refresh_token else None

            if new_token:
                result = await fetch_and_analyze_emails(user_email, new_token, skip_existing=False)

            if not new_token or result["error"] == "token_expired":
                return RedirectResponse(url="/auth/login", status_code=302)

        if result["error"]:
            print(f"❌ Refresh failed, keeping existing emails: {result['error']}")
            return RedirectResponse(url="/dashboard?error=refresh_failed", status_code=302)

        await run_in_threadpool(replace_all_emails_for_user, user_email, result["emails"])

    except Exception as e:
        print(f"❌ Refresh error: {e}")
        import traceback; traceback.print_exc()

    return RedirectResponse(url="/dashboard", status_code=302)


#  ROUTE 6: Filter

@app.get("/filter", response_class=HTMLResponse)
async def filter_emails(
    request: Request,
    priority: str = None,
    category: str = None,
    read: str = None,
):
    user_email = get_current_user(request)
    if not user_email:
        return RedirectResponse(url="/", status_code=302)

    emails = []
    stats  = _empty_stats()

    try:
        emails = await run_in_threadpool(get_filtered_emails, user_email, priority, category, read)
        stats  = await run_in_threadpool(get_stats_for_user, user_email)
    except Exception as e:
        print(f"DB error: {e}")

    return templates.TemplateResponse(request, "dashboard.html", {
        "user_email":    user_email,
        "user_name":     request.session.get("user_name", "User"),
        "user_picture":  request.session.get("user_picture", ""),
        "emails":        emails,
        "stats":         stats,
        "active_filter": priority or category or read or "all",
        "title":         "Dashboard — Email Intelligence",
    })


#  ROUTE 7: Logout

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)


#  ROUTE 8: Health Check

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "Email Intelligence System", "version": "1.0.0"}


#  ROUTE 9: Search

@app.get("/search", response_class=HTMLResponse)
async def search_emails(request: Request, q: str = ""):
    user_email = get_current_user(request)
    if not user_email:
        return RedirectResponse(url="/", status_code=302)

    emails = []
    stats  = _empty_stats()

    try:
        emails = await run_in_threadpool(db_search, user_email, q)
        stats  = await run_in_threadpool(get_stats_for_user, user_email)
    except Exception as e:
        print(f"Search error: {e}")

    return templates.TemplateResponse(request, "dashboard.html", {
        "user_email":    user_email,
        "user_name":     request.session.get("user_name", "User"),
        "user_picture":  request.session.get("user_picture", ""),
        "emails":        emails,
        "stats":         stats,
        "active_filter": "all",
        "search_query":  q,
        "title":         f"Search: {q} — Email Intelligence",
    })


#  HELPER

def _empty_stats():
    return {"total":0,"unread":0,"read":0,"high":0,"medium":0,"low":0,
            "work":0,"finance":0,"promotions":0,"social":0,"newsletters":0,"other":0}


#  STARTUP

@app.on_event("startup")
async def startup_event():
    print("🚀 Email Intelligence System starting up...")
    if init_db is None:
        print("❌ Database module failed to import earlier — see the error above. Skipping init_db().")
    else:
        try:
            init_db()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ init_db() ran but failed: {e}")
            import traceback; traceback.print_exc()
    print("✅ Server ready! Visit: http://localhost:8000")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)