<div align="center">

# 📧 NexInbox — AI-Powered Email Intelligence System

**Automatically classify, prioritize, and summarize your Gmail inbox using the power of Large Language Models.**

[![Python](https://img.shields.io/badge/Python-3.12-4f8ef7?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-f97316?style=flat-square)](https://groq.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Supabase](https://img.shields.io/badge/Hosted_on-Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com)
[![Google OAuth](https://img.shields.io/badge/Auth-Google_OAuth_2.0-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/identity)
[![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=flat-square)](https://nexinbox.onrender.com)
[![License](https://img.shields.io/badge/License-MIT-a78bfa?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Live-34d399?style=flat-square)](https://nexinbox.onrender.com)

---

*Sign in with Google → Fetch your inbox → Let AI triage it for you.*

🌐 **Live Demo:** [nexinbox.onrender.com](https://nexinbox.onrender.com)

</div>

---

## 🎬 Demo

> 📽️ **Insert project demo GIF here**
>
> **What to record:**
> - Open the landing page at nexinbox.onrender.com
> - Click "Continue with Google" and complete login
> - Click "Fetch Emails" and watch the inbox load with AI labels
> - Show the dashboard with priority badges and category labels
> - Click a sidebar filter (e.g., "High Priority")
> - Open an individual email to show the AI summary
>
> **Recommended tool:** [LICEcap](https://www.cockos.com/licecap/) or [Kap](https://getkap.co/)
> **Recommended size:** 1200×700px, under 10MB

---

## 📌 Table of Contents

- [Problem Statement](#-problem-statement)
- [What It Does](#-what-it-does)
- [Screenshots](#-screenshots)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation Guide](#-installation-guide)
- [Configuration](#-configuration)
- [How It Works](#-how-it-works)
- [Module Interaction](#-module-interaction)
- [API Details](#-api-details)
- [Database](#-database)
- [AI Engine](#-ai-engine)
- [Security](#-security)
- [Performance](#-performance)
- [Error Handling](#-error-handling)
- [Future Improvements](#-future-improvements)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)
- [Acknowledgements](#-acknowledgements)

---

## 🚨 Problem Statement

The average professional receives **120+ emails per day**. Most email clients show them in chronological order — meaning a critical interview invitation sits right next to a Zomato discount offer with no distinction between them.

**The result:**
- Important emails get buried and missed
- Hours are wasted manually scanning the inbox
- There is no instant sense of what actually needs attention

**NexInbox solves this** by connecting to your Gmail, automatically reading every new email, and using a Large Language Model (LLM) to instantly answer three questions about each one:

1. **How urgent is this?** → High / Medium / Low priority
2. **What kind of email is this?** → Work, Finance, Promotions, Social, Newsletters, Other
3. **What is it actually about?** → A one-line AI-generated summary

The result is a clean, filterable dashboard where your most important emails are always on top — with data stored permanently in the cloud so nothing is ever lost.

**Who benefits:** Students, job seekers, professionals, and anyone managing a high-volume inbox.

---

## ✨ What It Does


|
 Feature 
|
 Description 
|
|
---
|
---
|
|
 🔐 
**
Google Login
**
|
 Secure sign-in via Google OAuth 2.0 — no passwords stored 
|
|
 📬 
**
Gmail Fetch
**
|
 Retrieves your latest 30 inbox emails via the Gmail API 
|
|
 🤖 
**
AI Priority Tagging
**
|
 Every email labelled High 🔴 / Medium 🟡 / Low 🟢 automatically 
|
|
 🗂️ 
**
Smart Categorization
**
|
 Work, Finance, Promotions, Social, Newsletters, Other 
|
|
 📝 
**
AI Summaries
**
|
 One-sentence plain-English summary of each email 
|
|
 📊 
**
Live Dashboard
**
|
 Stat cards: total, read, unread, priority & category breakdowns 
|
|
 🔍 
**
Search
**
|
 Case-insensitive search by sender, subject, or AI summary 
|
|
 🎛️ 
**
Sidebar Filters
**
|
 Instantly filter by priority, category, or read status 
|
|
 🔄 
**
Smart Re-fetch
**
|
 Only downloads emails not already in the database — no duplicates 
|
|
 ☁️ 
**
Persistent Cloud DB
**
|
 PostgreSQL on Supabase — data survives server restarts 
|
|
 👥 
**
Multi-user
**
|
 Each user sees only their own emails, fully isolated 
|
|
 🛡️ 
**
Fallback Classifier
**
|
 Keyword-based backup when AI API is unavailable 
|
|
 📐 
**
Accuracy Evaluator
**
|
 Standalone tool to measure and improve AI classification accuracy 
|

---

## 📸 Screenshots

### 1. Landing Page

> 📷 **Insert screenshot here**
>
> **What it should show:** The NexInbox landing page with "Continue with Google" button and the animated inbox preview on the right
> **When to capture:** Before logging in, at `https://nexinbox.onrender.com`

---

### 2. Google OAuth Consent Screen

> 📷 **Insert screenshot here**
>
> **What it should show:** Google's permission screen asking to allow Gmail read access
> **When to capture:** After clicking "Continue with Google"

---

### 3. Dashboard — Full Inbox View

> 📷 **Insert screenshot here**
>
> **What it should show:** Main dashboard with stat cards (Total, Unread, High Priority), sidebar filters, and email list with priority badges 🔴🟡🟢 and category labels
> **When to capture:** After emails have been fetched and classified

---

### 4. Dashboard — High Priority Filter

> 📷 **Insert screenshot here**
>
> **What it should show:** Dashboard filtered to show only High priority emails
> **When to capture:** After clicking "High Priority" in the sidebar

---

### 5. Individual Email Detail View

> 📷 **Insert screenshot here**
>
> **What it should show:** Full email detail page with AI-generated summary box, priority badge, category label, sender info, and email body
> **When to capture:** After clicking any email in the list

---

### 6. Search Results

> 📷 **Insert screenshot here**
>
> **What it should show:** Dashboard filtered by a keyword (e.g., "interview") with matching emails
> **When to capture:** After typing a keyword in the search bar

---

### 7. Supabase Dashboard

> 📷 **Insert screenshot here**
>
> **What it should show:** The Supabase Table Editor showing the `emails` table with real classified email data — columns like priority, category, ai_summary visible
> **When to capture:** After fetching emails, from supabase.com → Table Editor

---

### 8. Terminal — AI Classification Logs

> 📷 **Insert screenshot here**
>
> **What it should show:** Terminal output during email fetch showing batch AI analysis, e.g., `📦 Processing batch 1 (10 emails)...` and `✅ Saved 30/30 emails to database`
> **When to capture:** During the first email fetch after login

---

## 🏗️ Architecture

### High-Level Architecture

┌─────────────────────────────────────────────────────────┐
│ USER │
│ (Browser at nexinbox.onrender.com) │
└────────────────────────┬────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│ FastAPI Backend (main.py) │
│ Routes: /, /dashboard, /email/{id}, /filter, /search │
└──────┬──────────┬──────────┬──────────┬─────────────────┘
│ │ │ │
▼ ▼ ▼ ▼
┌─────────┐ ┌────────┐ ┌──────┐ ┌──────────────┐
│ auth.py │ │gmail.py│ │ ai.py│ │ database.py │
│ Google │ │ Gmail │ │ Groq │ │ psycopg2 │
│ OAuth │ │ API │ │ API │ │ PostgreSQL │
└────┬────┘ └───┬────┘ └──┬───┘ └──────┬───────┘
│ │ │ │
▼ ▼ ▼ ▼
┌──────────────────────┐ ┌─────────────────────┐
│ Google APIs │ │ Supabase (Cloud) │
│ accounts.google.com │ │ PostgreSQL Database │
│ gmail.googleapis.com│ │ Permanent Storage │
└──────────────────────┘ └─────────────────────┘
│
▼
┌──────────────────┐
│ Groq API │
│ Llama 3.3 70B │
└──────────────────┘


> 📷 **Insert architecture diagram image here**
>
> **Recommended tool:** [Excalidraw](https://excalidraw.com) or [draw.io](https://draw.io)
> **What it should show:** Color-coded visual of the text diagram above with arrows showing data flow between each layer

---

### Data Flow Diagram

User clicks "Login"
│
▼
Google OAuth → Access Token + Refresh Token
│
▼
User clicks "Fetch Emails"
│
▼
Gmail API → Raw email list (up to 30 messages)
│
▼
Skip emails already in PostgreSQL (deduplication)
│
▼
Parse new emails (subject, sender, body, date)
│
▼
Send to Groq API in batches of 10
│
▼
AI returns: priority + category + summary (JSON)
│
▼
Bulk save to PostgreSQL on Supabase ☁️
│
▼
Render on dashboard (Jinja2 templates)
│
▼
User filters / searches / reads emails


---

## 🛠️ Tech Stack

| Layer | Technology | Version | Why It Was Chosen |
|---|---|---|---|
| **Backend Framework** | FastAPI | 0.136 | Async-native, fast, perfect for building REST routes and serving HTML templates |
| **Frontend Templating** | Jinja2 | 3.1.6 | Server-side HTML rendering directly from FastAPI — no separate frontend needed |
| **Database** | PostgreSQL | Latest | Production-grade relational database — persistent, reliable, cloud-hosted |
| **Cloud Database Host** | Supabase | — | Free managed PostgreSQL hosting — data persists across server restarts unlike SQLite |
| **Database Driver** | psycopg2-binary | 2.9.9 | Python driver for connecting to PostgreSQL databases |
| **Authentication** | Google OAuth 2.0 | — | Industry-standard secure login using existing Google accounts |
| **Email API** | Gmail API (Google) | v1 | Official read-only access to Gmail inbox |
| **AI / LLM** | Groq API (Llama 3.3 70B) | — | Extremely fast LLM inference with high-quality email classification |
| **HTTP Client** | httpx | 0.28.1 | Async HTTP client for all external API calls |
| **Session Management** | Starlette SessionMiddleware | 1.2.1 | Signed cookie-based sessions to keep users logged in |
| **Secret Management** | python-dotenv | 1.2.2 | Loads credentials from `.env` — secrets never hardcoded |
| **ASGI Server** | Uvicorn | 0.49.0 | Production-ready async server for FastAPI |
| **Deployment** | Render | — | Auto-deploys from GitHub on every push — free tier available |
| **Language** | Python | 3.12 | Main language for backend, AI calls, and database operations |

---

## 📁 Project Structure

```text
nexinbox/
│
├── main.py                 ← App entry point: all routes and startup logic
├── auth.py                 ← Google OAuth 2.0 login and token management
├── gmail.py                ← Gmail API integration and email parsing
├── ai.py                   ← Groq AI classification engine
├── database.py             ← PostgreSQL database functions (schema, CRUD, search)
├── evaluate_ai.py          ← Standalone AI accuracy evaluation script
│
├── .env                    ← Secret keys and API credentials (never commit this)
├── .gitignore              ← Excludes .env, __pycache__, venv from Git
├── Procfile                ← Tells Render how to start the app
├── requirements.txt        ← All Python package dependencies
│
├── templates/
│   ├── index.html          ← Landing page (login screen)
│   ├── dashboard.html      ← Main email dashboard with filters and stats
│   └── email_detail.html   ← Individual email view with AI summary
│
└── static/
    └── css/                ← Stylesheets for all pages
```

### File-by-File Breakdown

| File | Purpose | Runs When | Interacts With |
|---|---|---|---|
| `main.py` | All URL routes, app startup, session logic | Every request | auth.py, gmail.py, ai.py, database.py, templates/ |
| `auth.py` | Google login redirect, callback, token exchange | User clicks Login or token expires | Google OAuth API, database.py |
| `gmail.py` | Fetches inbox from Gmail API, parses raw messages | User clicks "Fetch Emails" | Gmail API, ai.py, database.py |
| `ai.py` | Sends emails to Groq for priority/category/summary | After Gmail fetch | Groq API (Llama 3.3 70B) |
| `database.py` | All PostgreSQL operations via psycopg2 | On startup and every data operation | Supabase PostgreSQL, called by main.py, gmail.py, auth.py |
| `evaluate_ai.py` | Manual accuracy testing tool | Run manually: `python evaluate_ai.py` | database.py |
| `Procfile` | Tells Render the start command | Render deployment | Uvicorn, main.py |
| `.env` | All secret credentials | Loaded at startup | main.py, auth.py, ai.py, database.py |
| `requirements.txt` | All Python packages | `pip install -r requirements.txt` | pip / virtual environment |
| `templates/` | Jinja2 HTML files rendered by FastAPI | Every page load | main.py |
| `static/css/` | Styling for all pages | Loaded by browser | templates/ |

---

## 🚀 Installation Guide

### Step 1 — Prerequisites

Make sure you have:
- **Python 3.10+** → [Download](https://www.python.org/downloads/)
- **Git** → [Download](https://git-scm.com/downloads)
- A **Google Account** (Gmail)
- A **Groq account** → [Sign up free](https://console.groq.com)
- A **Supabase account** → [Sign up free](https://supabase.com)

```bash
python --version   # Should show 3.10 or higher
```

---

### Step 2 — Clone the Repository

```bash
git clone https://github.com/Subham093/nexinbox.git
cd nexinbox
```

---

### Step 3 — Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac/Linux
source venv/bin/activate
```

> ✅ You'll see `(venv)` at the start of your terminal when active.

---

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 5 — Set Up Supabase (PostgreSQL)

1. Go to [https://supabase.com](https://supabase.com) → **"New Project"**
2. Give it a name (e.g., `nexinbox`) and set a database password
3. Once created, go to **Settings → Database**
4. Copy the **Connection String (URI)** — it looks like:

postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres

5. This is your `DATABASE_URL`

---

### Step 6 — Set Up Google Cloud Console

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Create new project → Enable **Gmail API**
3. Go to **Credentials → Create OAuth 2.0 Client ID** (Web application)
4. Add redirect URI: `http://localhost:8000/auth/callback`
5. Copy your **Client ID** and **Client Secret**
6. Add your Gmail as a **Test User** in OAuth consent screen

---

### Step 7 — Get Groq API Key

1. Sign up at [https://console.groq.com](https://console.groq.com)
2. Go to **API Keys → Create API Key**
3. Copy the key (starts with `gsk_...`)

---

### Step 8 — Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-random-secret-key-here
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret
GROQ_API_KEY=gsk_your-groq-key
DATABASE_URL=postgresql://postgres:password@db.xxxx.supabase.co:5432/postgres
REDIRECT_URI=http://localhost:8000/auth/callback
```

---

### Step 9 — Run the App

```bash
uvicorn main:app --reload
```

Visit **[http://localhost:8000](http://localhost:8000)** 🎉

---

## ⚙️ Configuration

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Signs session cookies — any long random string |
| `GOOGLE_CLIENT_ID` | ✅ | From Google Cloud Console OAuth credentials |
| `GOOGLE_CLIENT_SECRET` | ✅ | From Google Cloud Console OAuth credentials |
| `GROQ_API_KEY` | ✅ | From console.groq.com — starts with `gsk_` |
| `DATABASE_URL` | ✅ | PostgreSQL connection URL from Supabase |
| `REDIRECT_URI` | ✅ | `http://localhost:8000/auth/callback` locally, `https://nexinbox.onrender.com/auth/callback` on Render |

> ⚠️ Never commit your `.env` file to GitHub. It's already excluded by `.gitignore`.

---

## ⚙️ How It Works

1. **Landing Page** — You visit the app. If not logged in, landing page is shown.
2. **Google Login** — Click "Continue with Google". App redirects to Google's consent screen requesting read-only Gmail access.
3. **OAuth Callback** — Google redirects back with an auth code. App exchanges it for access + refresh tokens. Your profile is saved to PostgreSQL on Supabase.
4. **Dashboard** — You're redirected to the dashboard. Empty on first visit.
5. **Fetch Emails** — App calls Gmail API with your token. Gets 30 latest inbox messages. Checks PostgreSQL to skip already-stored ones.
6. **Email Parsing** — New emails are parsed: MIME headers decoded, Base64 body extracted, HTML stripped, clean text produced.
7. **AI Classification** — Parsed emails sent to Groq API in batches of 10. Llama 3.3 70B returns priority, category, and summary as JSON.
8. **Database Storage** — All classified emails bulk-saved to PostgreSQL on Supabase. Unique constraint prevents duplicates.
9. **Dashboard Render** — Stat cards, email list with priority badges, sidebar filters — all from PostgreSQL.
10. **Filter / Search / Read** — Filter by priority/category/read status. Search by keyword (case-insensitive via `ILIKE`). Click email → detail view → marked as read.

---

## 🔗 Module Interaction

Browser Request
│
▼
main.py (FastAPI Router)
│
├─── /auth/login ──────► auth.py ──────► Google OAuth API
│ │
│ ▼
│ database.py ──► Supabase PostgreSQL ☁️
│
├─── /fetch-emails ────► gmail.py ──────► Gmail API
│ │
│ ▼
│ ai.py ──────────► Groq API (Llama 3.3)
│ │
│ ▼
│ database.py ──► Supabase PostgreSQL ☁️
│
├─── /dashboard ───────► database.py ──► Supabase PostgreSQL ☁️
│ │
│ ▼
│ templates/dashboard.html (Jinja2)
│
├─── /filter ──────────► database.py (get_filtered_emails)
├─── /search ──────────► database.py (search_emails with ILIKE)
└─── /email/{id} ──────► database.py (get_email_by_id + mark_as_read)


---

## 🌐 API Details

### External APIs

#### Gmail API

| Endpoint | Method | Purpose |
|---|---|---|
| `/messages` | GET | List message IDs (max 30) |
| `/messages/{id}` | GET | Fetch full message by ID |

**Base URL:** `https://gmail.googleapis.com/gmail/v1/users/me`
**Auth:** Bearer token (Google OAuth access token)

---

#### Groq API

**Endpoint:** `https://api.groq.com/openai/v1/chat/completions`
**Model:** `llama-3.3-70b-versatile`

**Request:**
```json
{
  "model": "llama-3.3-70b-versatile",
  "messages": [{ "role": "user", "content": "<classification prompt>" }],
  "temperature": 0.1,
  "max_tokens": 2000
}
```

**Response:**
```json
[
  { "index": 0, "priority": "high", "category": "Work", "summary": "Interview scheduled for Monday at 10am." },
  { "index": 1, "priority": "low", "category": "Promotions", "summary": "Myntra offering 50% off this weekend." }
]
```

---

### Internal App Routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/` | GET | No | Landing page |
| `/auth/login` | GET | No | Redirect to Google login |
| `/auth/callback` | GET | No | Handle Google OAuth response |
| `/dashboard` | GET | Yes | Main email dashboard |
| `/email/{id}` | GET | Yes | Individual email detail |
| `/fetch-emails` | POST | Yes | Fetch new emails from Gmail |
| `/refresh-emails` | POST | Yes | Wipe and re-fetch all emails |
| `/filter` | GET | Yes | Filter by priority/category/read |
| `/search` | GET | Yes | Search emails by keyword |
| `/logout` | GET | Yes | Clear session |
| `/health` | GET | No | Health check |

---

## 🗄️ Database

**Database:** PostgreSQL hosted on **Supabase** (cloud)

**Why PostgreSQL over SQLite?**

| | SQLite (old) | PostgreSQL on Supabase (current) |
|---|---|---|
| Storage | Local file inside app | Cloud — separate from app server |
| Survives restart | ❌ Wiped on Render restart | ✅ Always persists |
| Multi-user | Limited | ✅ Production-grade |
| Search | Basic LIKE | ✅ Case-insensitive ILIKE |
| Scale | Single file | ✅ Scales to millions of rows |

---

### Table: `users`

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL | Auto-incrementing primary key |
| `email` | TEXT (UNIQUE) | Google email — one row per user |
| `name` | TEXT | Full name from Google |
| `picture` | TEXT | Profile picture URL |
| `access_token` | TEXT | Current Gmail API access token |
| `refresh_token` | TEXT | Long-lived token for renewal |
| `created_at` | TIMESTAMP | First login time |
| `last_login` | TIMESTAMP | Most recent login time |

---

### Table: `emails`

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL | Auto-incrementing primary key |
| `gmail_id` | TEXT | Gmail's unique message ID |
| `user_email` | TEXT | Which user this belongs to |
| `subject` | TEXT | Email subject line |
| `sender` | TEXT | Display name of sender |
| `sender_email` | TEXT | Email address of sender |
| `snippet` | TEXT | Short preview text |
| `body` | TEXT | Full plain-text body |
| `date` | TEXT | Date email was received |
| `is_read` | INTEGER | 0 = unread, 1 = read |
| `priority` | TEXT | `high`, `medium`, or `low` |
| `category` | TEXT | `Work`, `Finance`, `Promotions`, etc. |
| `ai_summary` | TEXT | AI-generated one-line summary |
| `fetched_at` | TIMESTAMP | When NexInbox saved this email |

**Key Constraint:** `UNIQUE(gmail_id, user_email)` — prevents duplicate emails per user.

**Relationship:**

users.email (1) ──── (many) emails.user_email


---

## 🤖 AI Engine

### Model
**Groq API** running **Meta's Llama 3.3 70B Versatile**

- **Why Groq?** Fastest LLM inference available — often under 1 second. Free tier generous.
- **Why Llama 3.3 70B?** Strong instruction-following for nuanced classification tasks.

### Prompt Design
- **Strict label sets** — only `high/medium/low` and 6 fixed categories allowed
- **Explicit edge-case rules** — e.g., hiring alerts → Work, OTPs → Other
- **Temperature 0.1** — near-deterministic, consistent results
- **JSON-only response** — no surrounding text, easy to parse

### Input / Output

**Input to AI:**
```json
[{ "index": 0, "subject": "Interview Monday", "sender": "hr@company.com", "preview": "Your technical interview..." }]
```

**Output from AI:**
```json
[{ "index": 0, "priority": "high", "category": "Work", "summary": "Technical interview scheduled for Monday 10am." }]
```

### Fallback Classifier
If Groq API fails, `assign_defaults()` uses keyword matching on subject/sender/snippet to assign reasonable priority and category — app never crashes due to AI failure.

### Limitations
- Short or vague emails may be misclassified
- Groq free tier has rate limits (handled by 6-second batch delay)
- Classification accuracy ~70-85% depending on email type

### Evaluate Accuracy
```bash
python evaluate_ai.py
```
Compares AI labels vs your manual corrections. Prints accuracy %, confusion matrix, per-category breakdown.

---

## 🔒 Security

| Concern | How Handled |
|---|---|
| **Authentication** | Google OAuth 2.0 — no passwords ever stored |
| **Session security** | Signed cookies via Starlette SessionMiddleware |
| **Secret management** | All credentials in `.env`, excluded from Git |
| **User isolation** | Every DB query scoped to `user_email` |
| **Gmail access** | Read-only scope — cannot send, delete, or modify |
| **Token expiry** | 401 from Gmail → session cleared → redirect to login |
| **Database** | Hosted on Supabase with connection string auth |

---

## ⚡ Performance

| Optimization | Detail |
|---|---|
| **Batch AI requests** | 10 emails per Groq call — reduces total API calls by 10x |
| **Deduplication before fetch** | Existing IDs loaded once, checked before parsing |
| **Bulk DB insert** | All new emails saved in one transaction |
| **Rate-limit awareness** | 6-second delay between batches prevents Groq errors |
| **Incremental fetch** | Only new emails fetched and classified on re-visits |
| **ILIKE search** | PostgreSQL native case-insensitive search — faster than Python-side filtering |
| **Cloud DB** | Supabase PostgreSQL — separate from app server, no I/O bottleneck |

---

## 🛡️ Error Handling

| Scenario | How Handled |
|---|---|
| User denies Google login | Redirect to `/?error=login_denied` |
| Token exchange fails | Redirect to `/?error=token_failed` |
| Gmail returns 401 (expired token) | Session cleared, redirect to login |
| Groq returns non-200 | Falls back to keyword `assign_defaults` |
| Groq returns malformed JSON | Caught by JSONDecodeError, falls back to defaults |
| Individual email parse error | Email skipped, others continue |
| DB save error | Rolled back, error logged, app continues |
| Email not found (detail page) | Returns HTTP 404 |
| No emails in DB | Dashboard renders with zeroed stats |

---

## 🔮 Future Improvements

- [ ] **Multi-account support** — connect multiple Gmail accounts
- [ ] **AI reply drafting** — one-click AI-generated reply suggestions
- [ ] **Push notifications** — alerts for new high-priority emails
- [ ] **Calendar integration** — detect meeting invitations, add to Google Calendar
- [ ] **Unsubscribe automation** — one-click unsubscribe from mailing lists
- [ ] **Email threading** — group by conversation thread
- [ ] **Vector search** — semantic search using embeddings (pgvector on Supabase)
- [ ] **Custom rules** — user-defined classification rules
- [ ] **Export to CSV** — download classified inbox as spreadsheet
- [ ] **Docker support** — containerize for portable deployment
- [ ] **GitHub Actions CI** — auto syntax check on every push

---

## 🤝 Contributing

```bash
# 1. Fork the repo on GitHub

# 2. Clone your fork
git clone https://github.com/Subham093/nexinbox.git
cd nexinbox

# 3. Create a branch
git checkout -b feature/your-feature-name

# 4. Make changes, then commit
git commit -m "feat: add your feature"

# 5. Push and open a Pull Request
git push origin feature/your-feature-name
```

**Commit format:**

feat: new feature
fix: bug fix
docs: documentation
refactor: code restructure


---

## 📄 License

MIT License — free to use, modify, and distribute.
See [LICENSE](LICENSE) for details.

---

## 👤 Author

**Subham Maheswari Jena**

- 🎓 Intern at NALCO, Corporate Bhawan
- 🐙 [GitHub](https://github.com/Subham093)
- 💼 [LinkedIn](https://linkedin.com/in/yourprofile)
- 📧 [your.email@gmail.com](mailto:your.email@gmail.com)

---

## 🙏 Acknowledgements

- [**Groq**](https://groq.com) — Ultra-fast LLM inference
- [**Meta AI**](https://ai.meta.com) — Llama 3.3 70B open-weight model
- [**Google**](https://developers.google.com) — Gmail API and OAuth 2.0
- [**Supabase**](https://supabase.com) — Free managed PostgreSQL hosting
- [**FastAPI**](https://fastapi.tiangolo.com) — Python web framework
- [**Render**](https://render.com) — Free deployment platform
- [**NALCO, Corporate Bhawan**](https://nalcoindia.com) — Internship opportunity

---

<div align="center">

Built with ❤️ during an internship at NALCO, Corporate Bhawan

🌐 **[nexinbox.onrender.com](https://nexinbox.onrender.com)**

⭐ If this helped you, give it a star on GitHub!

</div>