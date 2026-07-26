#  main.py — Entry Point

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

load_dotenv()

try:
    from database import init_db
except ImportError as e:
    print(f"⚠️  Could not import database.py — real reason: {e}")
    init_db = None

try:
    from auth import router as auth_router
except ImportError as e:
    print(f"⚠️  Could not import auth.py — real reason: {e}")
    auth_router = None

try:
    from gmail import router as gmail_router
except ImportError as e:
    print(f"⚠️  Could not import gmail.py — real reason: {e}")
    gmail_router = None

# ══════════════════════════════════════════════════
app = FastAPI(title="NexInbox", version="1.0.0")

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-please")
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=86400,
    https_only=False,
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
        from database import get_emails_for_user, get_stats_for_user
        emails = get_emails_for_user(user_email)
        stats  = get_stats_for_user(user_email)
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
        from database import get_email_by_id, mark_email_as_read
        email_data = get_email_by_id(email_id, user_email)
        if email_data:
            mark_email_as_read(email_id, user_email)
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


#  ROUTE 4: Fetch Emails (SMART)

@app.post("/fetch-emails")
async def fetch_emails(request: Request):
    user_email = get_current_user(request)
    if not user_email:
        return RedirectResponse(url="/", status_code=302)

    access_token = request.session.get("access_token")
    if not access_token:
        # No token in session → force re-login
        request.session.clear()
        return RedirectResponse(url="/auth/login", status_code=302)

    try:
        from database import get_emails_for_user
        from gmail import fetch_and_store_emails

        existing_emails = get_emails_for_user(user_email)
        existing_count  = len(existing_emails)

        if existing_count == 0:
            print(f"📬 First fetch for {user_email}")
            result = await fetch_and_store_emails(
                user_email=user_email,
                access_token=access_token,
                mode="full"
            )
        else:
            print(f"🔄 Refresh fetch for {user_email}")
            result = await fetch_and_store_emails(
                user_email=user_email,
                access_token=access_token,
                mode="refresh"
            )

        # ── If token expired → clear session and re-login ────
        if result.get("error") == "token_expired":
            print("🔑 Token expired — redirecting to login")
            request.session.pop("access_token", None)
            return RedirectResponse(url="/auth/login", status_code=302)

        new_count = result.get("new", 0)
        print(f"✅ {new_count} new emails added" if new_count > 0 else "✅ Inbox up to date")

    except Exception as e:
        print(f"❌ Fetch error: {e}")
        import traceback; traceback.print_exc()

    return RedirectResponse(url="/dashboard", status_code=302)


#  ROUTE 5: Force Refresh (wipe + re-fetch)

@app.post("/refresh-emails")
async def refresh_emails(request: Request):
    user_email = get_current_user(request)
    if not user_email:
        return RedirectResponse(url="/", status_code=302)

    access_token = request.session.get("access_token")
    if not access_token:
        request.session.clear()
        return RedirectResponse(url="/auth/login", status_code=302)

    try:
        from database import delete_emails_for_user
        from gmail import fetch_and_store_emails
        print(f"🔄 Force refresh for {user_email}")
        delete_emails_for_user(user_email)
        result = await fetch_and_store_emails(
            user_email=user_email,
            access_token=access_token,
            mode="full"
        )
        if result.get("error") == "token_expired":
            request.session.pop("access_token", None)
            return RedirectResponse(url="/auth/login", status_code=302)
    except Exception as e:
        print(f"❌ Refresh error: {e}")

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
        from database import get_filtered_emails, get_stats_for_user
        emails = get_filtered_emails(
            user_email=user_email,
            priority=priority,
            category=category,
            read_status=read
        )
        stats = get_stats_for_user(user_email)
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


#  ROUTE: Search  GET /search?q=keyword

@app.get("/search", response_class=HTMLResponse)
async def search_emails(request: Request, q: str = ""):
    user_email = get_current_user(request)
    if not user_email:
        return RedirectResponse(url="/", status_code=302)

    emails = []
    stats  = _empty_stats()

    try:
        from database import search_emails as db_search, get_stats_for_user
        emails = db_search(user_email=user_email, query=q)
        stats  = get_stats_for_user(user_email)
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