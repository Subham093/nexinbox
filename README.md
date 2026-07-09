<div align="center">

# 📧 NexInbox — AI-Powered Email Intelligence System

**Automatically classify, prioritize, and summarize your Gmail inbox using the power of Large Language Models.**

[![Python](https://img.shields.io/badge/Python-3.12-4f8ef7?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-f97316?style=flat-square)](https://groq.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Google OAuth](https://img.shields.io/badge/Auth-Google_OAuth_2.0-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/identity)
[![License](https://img.shields.io/badge/License-MIT-a78bfa?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Live-34d399?style=flat-square)]()

---

*Sign in with Google → Fetch your inbox → Let AI triage it for you.*

</div>

---

## 🎬 Demo

> 📽️ **Insert project demo GIF here**
>
> **What to record:**
> - Open the landing page
> - Click "Sign in with Google" and complete login
> - Click "Fetch Emails" and watch the inbox load
> - Show the dashboard with priority badges and category labels
> - Click a sidebar filter (e.g., "High Priority") to show filtered results
> - Open an individual email to show the AI summary
>
> **Recommended tool:** [LICEcap](https://www.cockos.com/licecap/) or [Kap](https://getkap.co/) (Mac)  
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

The result is a clean, filterable dashboard where your most important emails are always on top.

**Who benefits:** Students, job seekers, professionals, and anyone managing a high-volume inbox.

---

## ✨ What It Does

| Feature | Description |
|---|---|
| 🔐 **Google Login** | Secure sign-in via Google OAuth 2.0 — no passwords stored |
| 📬 **Gmail Fetch** | Retrieves your latest 30 inbox emails via the Gmail API |
| 🤖 **AI Priority Tagging** | Every email labelled High 🔴 / Medium 🟡 / Low 🟢 automatically |
| 🗂️ **Smart Categorization** | Work, Finance, Promotions, Social, Newsletters, Other |
| 📝 **AI Summaries** | One-sentence plain-English summary of each email |
| 📊 **Live Dashboard** | Stat cards: total, read, unread, priority & category breakdowns |
| 🔍 **Search** | Search by sender, subject, or AI summary |
| 🎛️ **Sidebar Filters** | Instantly filter by priority, category, or read status |
| 🔄 **Smart Re-fetch** | Only downloads emails not already in the database — no duplicates |
| 👥 **Multi-user** | Each user sees only their own emails, fully isolated |
| 🛡️ **Fallback Classifier** | Keyword-based backup when AI API is unavailable |
| 📐 **Accuracy Evaluator** | Standalone tool to measure and improve AI classification accuracy |

---

## 📸 Screenshots

### 1. Landing Page

> 📷 **Insert screenshot here**
>
> **What it should show:** The NexInbox landing page with the "Sign in with Google" button  
> **When to capture:** Before logging in, at `http://localhost:8000`

---

### 2. Google OAuth Consent Screen

> 📷 **Insert screenshot here**
>
> **What it should show:** Google's permission screen asking to allow Gmail read access  
> **When to capture:** After clicking "Sign in with Google"

---

### 3. Dashboard — Full Inbox View

> 📷 **Insert screenshot here**
>
> **What it should show:** The main dashboard with stat cards at the top (Total, Unread, High Priority, etc.), the sidebar filter panel on the left, and the email list on the right with priority badges (🔴🟡🟢) and category labels  
> **When to capture:** After emails have been fetched and classified

---

### 4. Dashboard — High Priority Filter Active

> 📷 **Insert screenshot here**
>
> **What it should show:** The same dashboard with only High priority emails visible, sidebar "High" filter highlighted  
> **When to capture:** After clicking the "High Priority" filter in the sidebar

---

### 5. Individual Email Detail View

> 📷 **Insert screenshot here**
>
> **What it should show:** The full email detail page, including the AI-generated summary box, priority badge, category label, sender details, and full email body  
> **When to capture:** After clicking on any email in the dashboard list

---

### 6. Search Results

> 📷 **Insert screenshot here**
>
> **What it should show:** The dashboard filtered to show search results for a keyword (e.g., "interview"), with matching emails highlighted  
> **When to capture:** After typing a keyword in the search bar

---

### 7. Terminal — AI Classification in Progress

> 📷 **Insert screenshot here**
>
> **What it should show:** The terminal output during email fetch, showing batch AI analysis logs, e.g., `📦 Processing batch 1 (10 emails)...`  
> **When to capture:** During the first email fetch after login

---

### 8. Accuracy Evaluation Output (`evaluate_ai.py`)

> 📷 **Insert screenshot here**
>
> **What it should show:** Terminal output of `python evaluate_ai.py` showing the accuracy percentage, confusion matrix, and per-category breakdown  
> **When to capture:** After running the evaluation script

---

## 🏗️ Architecture

### High-Level Architecture
┌─────────────────────────────────────────────────────────┐
│                        USER                             │
│              (Browser at localhost:8000)                │
└────────────────────────┬────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│                     (main.py)                           │
│  Routes: /, /dashboard, /email/{id}, /filter, /search   │
└──────┬──────────┬──────────┬──────────┬─────────────────┘
│          │          │          │
▼          ▼          ▼          ▼
┌─────────┐ ┌────────┐ ┌──────┐ ┌──────────┐
│ auth.py │ │gmail.py│ │ ai.py│ │database.py│
│ Google  │ │ Gmail  │ │ Groq │ │  SQLite  │
│ OAuth   │ │  API   │ │ API  │ │    DB    │
└────┬────┘ └───┬────┘ └──┬───┘ └──────────┘
│          │         │
▼          ▼         ▼
┌─────────────────────────────────┐
│         Google APIs             │
│  accounts.google.com (OAuth)    │
│  gmail.googleapis.com (Email)   │
└─────────────────────────────────┘
│
▼
┌──────────────────┐
│   Groq API       │
│ Llama 3.3 70B    │
│ (Classification) │
└──────────────────┘

> 📷 **Insert architecture diagram image here**
>
> **What it should show:** A visual version of the text diagram above with color-coded boxes for each layer  
> **Recommended tool:** [Excalidraw](https://excalidraw.com), [draw.io](https://draw.io), or [Mermaid Live Editor](https://mermaid.live)

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
Skip emails already in DB (deduplication)
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
Save all to SQLite database
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
| **Backend Framework** | FastAPI | 0.136 | Async-native, fast, auto-generates API docs, great for building REST routes and serving HTML templates |
| **Frontend Templating** | Jinja2 | 3.1.6 | Server-side HTML rendering directly from FastAPI — no separate frontend framework needed |
| **Database** | SQLite | Built-in | Zero-configuration, file-based — perfect for single-server deployment; no need to install a database server |
| **Authentication** | Google OAuth 2.0 | — | Industry-standard; lets users log in securely with their existing Google account without storing passwords |
| **Email API** | Gmail API (Google) | v1 | Official read-only access to Gmail inbox — reliable, well-documented, supports message parsing |
| **AI / LLM** | Groq API (Llama 3.3 70B) | — | Extremely fast inference; Llama 3.3 70B gives high-quality classification with a strong understanding of email context |
| **HTTP Client** | httpx | 0.28.1 | Async HTTP client used for all external API calls (Google, Groq) — compatible with FastAPI's async model |
| **Session Management** | Starlette SessionMiddleware | 1.2.1 | Signed cookie-based sessions to keep users logged in across page loads |
| **Secret Management** | python-dotenv | 1.2.2 | Loads credentials from a `.env` file so secrets are never hardcoded in source code |
| **ASGI Server** | Uvicorn | 0.49.0 | Production-ready async server for running FastAPI applications |
| **Language** | Python | 3.12 | Widely used, excellent ecosystem for web APIs, AI/LLM calls, and data processing |
| **Version Control** | Git + GitHub | — | Source control and collaboration |

---

## 📁 Project Structure

```text
nexinbox/
│
├── main.py                 ← App entry point: all routes and startup logic
├── auth.py                 ← Google OAuth 2.0 login and token management
├── gmail.py                ← Gmail API integration and email parsing
├── ai.py                   ← Groq AI classification engine
├── database.py             ← SQLite database functions (schema, CRUD, search)
├── evaluate_ai.py          ← Standalone AI accuracy evaluation script
│
├── .env                    ← Secret keys and API credentials (never commit this)
├── .gitignore              ← Tells Git which files to ignore (.env, __pycache__, etc.)
├── requirements.txt        ← All Python package dependencies
├── email_intelligence.db   ← SQLite database file (auto-created on first run)
│
├── templates/
│   ├── index.html          ← Landing page (login screen)
│   ├── dashboard.html      ← Main email dashboard with filters and stats
│   └── email_detail.html   ← Individual email view with AI summary
│
└── static/
    └── css/                ← Stylesheets for dashboard and landing page
```

### File-by-File Breakdown

| File | Purpose | Runs When | Interacts With |
|---|---|---|---|
| `main.py` | Defines all URL routes, starts the app, handles session logic | Every request | auth.py, gmail.py, ai.py, database.py, templates/ |
| `auth.py` | Handles Google login redirect and callback, token exchange | User clicks "Login" or token expires | Google OAuth API, database.py, main.py |
| `gmail.py` | Fetches inbox from Gmail API, parses raw message data | User clicks "Fetch Emails" | Gmail API, ai.py, database.py |
| `ai.py` | Sends parsed emails to Groq for priority/category/summary | After Gmail fetch | Groq API (Llama 3.3 70B) |
| `database.py` | All SQLite operations: create tables, save/read/filter/search emails | On startup and every data operation | sqlite3 (built-in), called by main.py, gmail.py, auth.py |
| `evaluate_ai.py` | Manual accuracy testing tool — compare AI labels vs human labels | Run manually: `python evaluate_ai.py` | database.py |
| `.env` | Stores all secret credentials | Loaded at startup via python-dotenv | main.py, auth.py, ai.py |
| `requirements.txt` | Lists all Python packages needed to run the project | `pip install -r requirements.txt` | pip / virtual environment |
| `templates/` | Jinja2 HTML files rendered by FastAPI | On every page load | main.py (via Jinja2) |
| `static/css/` | Styling for all pages | Loaded by browser | templates/ |

---

## 🚀 Installation Guide

Follow every step in order. This guide assumes you have **no prior setup**.

---

### Step 1 — Prerequisites

Make sure you have the following installed:

- **Python 3.10 or higher** → [Download here](https://www.python.org/downloads/)
- **Git** → [Download here](https://git-scm.com/downloads)
- A **Google Account** (Gmail)
- A **Groq account** for the free AI API key → [Sign up here](https://console.groq.com)

To check your Python version, open a terminal and run:
```bash
python --version
```

---

### Step 2 — Clone the Repository

```bash
# Download the project to your computer
git clone https://github.com/yourusername/nexinbox.git

# Navigate into the project folder
cd nexinbox
```

---

### Step 3 — Create a Virtual Environment

A virtual environment keeps this project's packages separate from your system Python, preventing conflicts.

```bash
# Create the virtual environment (creates a folder called 'venv')
python -m venv venv

# Activate it on Windows
venv\Scripts\activate

# Activate it on Mac/Linux
source venv/bin/activate
```

> ✅ You'll know it's active when you see `(venv)` at the start of your terminal prompt.

---

### Step 4 — Install Dependencies

```bash
# Install all required Python packages listed in requirements.txt
pip install -r requirements.txt
```

This installs FastAPI, httpx, Jinja2, python-dotenv, and all other packages the project needs.

---

### Step 5 — Set Up Google Cloud Console

This is required to enable Gmail login and email access. Follow each sub-step:

**5a.** Go to [https://console.cloud.google.com](https://console.cloud.google.com)

**5b.** Click **"Select a Project"** → **"New Project"** → Give it a name (e.g., `NexInbox`) → Click **"Create"**

**5c.** In the left menu, go to **APIs & Services → Library**

**5d.** Search for **"Gmail API"** → Click it → Click **"Enable"**

**5e.** Go to **APIs & Services → OAuth consent screen**
- Choose **"External"** → Click **"Create"**
- Fill in App name: `NexInbox`, User support email: your Gmail
- Click **"Save and Continue"** through all steps

**5f.** Go to **APIs & Services → Credentials**
- Click **"+ Create Credentials"** → **"OAuth 2.0 Client ID"**
- Application type: **Web application**
- Under **Authorised redirect URIs**, add exactly:
http://localhost:8000/auth/callback
- Click **"Create"**
- Copy your **Client ID** and **Client Secret** — you'll need them next

**5g.** Go to **OAuth consent screen → Test users** → Add your Gmail address as a test user

---

### Step 6 — Get Your Groq API Key

1. Sign up for free at [https://console.groq.com](https://console.groq.com)
2. Go to **API Keys** → Click **"Create API Key"**
3. Copy the key (it starts with `gsk_...`)

---

### Step 7 — Configure Environment Variables

Create a file called `.env` in the root of the project:

```bash
# On Mac/Linux
touch .env

# On Windows (PowerShell)
New-Item .env
```

Open `.env` in any text editor and paste the following, replacing the placeholder values with your real credentials:

```env
SECRET_KEY=any-long-random-string-you-make-up
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret-here
GROQ_API_KEY=gsk_your-groq-api-key-here
```

> ⚠️ **Never share your `.env` file or commit it to GitHub.** The `.gitignore` file already excludes it.

---

### Step 8 — Run the Application

```bash
uvicorn main:app --reload
```

- `main` → refers to `main.py`
- `app` → refers to the FastAPI app object inside it
- `--reload` → automatically restarts the server when you edit a file (useful during development)

You should see:
INFO:     Uvicorn running on http://127.0.0.1:8000
✅ Database initialized successfully
✅ Server ready! Visit: http://localhost:8000

---

### Step 9 — Open in Browser

Visit: **[http://localhost:8000](http://localhost:8000)**

Click **"Sign in with Google"**, complete the login, then click **"Fetch Emails"** to load and classify your inbox.

---

## ⚙️ Configuration

All configuration is done through environment variables in the `.env` file. Here is every variable explained:

| Variable | Required | Description | Example Value |
|---|---|---|---|
| `SECRET_KEY` | ✅ Yes | Used to sign and encrypt session cookies. Make this a long random string. | `my-super-secret-key-abc123` |
| `GOOGLE_CLIENT_ID` | ✅ Yes | Your OAuth 2.0 Client ID from Google Cloud Console | `123456789-abc.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | ✅ Yes | Your OAuth 2.0 Client Secret from Google Cloud Console | `GOCSPX-abcdefghij` |
| `GROQ_API_KEY` | ✅ Yes | Your Groq API key for Llama 3.3 access | `gsk_abc123xyz` |

> 💡 **Tip:** You can generate a strong `SECRET_KEY` by running this in Python:
> ```python
> import secrets
> print(secrets.token_hex(32))
> ```

---

## ⚙️ How It Works

Here is the complete step-by-step flow from opening the app to seeing your classified inbox:

**Step 1 — Landing Page**
You visit `http://localhost:8000`. The app checks if you're already logged in (via session cookie). If not, it shows the landing page.

**Step 2 — Google Login**
You click "Sign in with Google". The app redirects you to Google's login page, requesting permission to read your Gmail (read-only).

**Step 3 — OAuth Callback**
After you approve, Google redirects you back to `/auth/callback` with a one-time authorization code. The app exchanges this for an access token (valid ~1 hour) and a refresh token (valid indefinitely). Your profile info (name, email, photo) is fetched and saved to the database. A session cookie is set in your browser.

**Step 4 — Dashboard (Empty)**
You're redirected to `/dashboard`. Since no emails have been fetched yet, it shows an empty inbox with zero stats.

**Step 5 — Fetch Emails**
You click "Fetch Emails". The app calls the Gmail API with your access token to retrieve your 30 most recent inbox messages. It checks which ones are already in the database and skips them (deduplication). Only new emails are parsed.

**Step 6 — Email Parsing**
Each new email is parsed: MIME headers are decoded, the body is extracted from the Base64-encoded payload, HTML tags are stripped, and the result is stored as a clean dictionary with subject, sender, snippet, body, and date.

**Step 7 — AI Classification**
The parsed emails are sent to the Groq API in batches of 10. The prompt instructs the Llama 3.3 70B model to return a JSON array with a priority, category, and summary for each email. The response is parsed, validated, and merged back into the email records.

**Step 8 — Database Storage**
All classified emails are bulk-saved to SQLite. The unique constraint on `(gmail_id, user_email)` ensures no duplicates ever enter the database.

**Step 9 — Dashboard Render**
The dashboard renders with stat cards, the full email list with priority badges and category chips, and a sidebar filter panel. All data comes directly from the database.

**Step 10 — Filter / Search / Read**
You can filter by priority, category, or read status. You can search by keyword. Clicking any email opens the detail view, marks it as read, and shows the full body plus the AI-generated summary.

---

## 🔗 Module Interaction
Browser Request
│
▼
main.py (FastAPI Router)
│
├─── /auth/login ──────► auth.py ──────► Google OAuth API
│                            │
│                            ▼
│                       database.py (save user + tokens)
│
├─── /fetch-emails ────► gmail.py ──────► Gmail API
│                            │
│                            ▼
│                        ai.py ──────────► Groq API (Llama 3.3)
│                            │
│                            ▼
│                       database.py (bulk save emails)
│
├─── /dashboard ───────► database.py (get_emails + get_stats)
│                            │
│                            ▼
│                       templates/dashboard.html (Jinja2)
│
├─── /filter ──────────► database.py (get_filtered_emails)
│
├─── /search ──────────► database.py (search_emails)
│
└─── /email/{id} ──────► database.py (get_email_by_id + mark_as_read)
│
▼
templates/email_detail.html

---

## 🌐 API Details

### External APIs Used

#### Gmail API

| Detail | Value |
|---|---|
| Base URL | `https://gmail.googleapis.com/gmail/v1/users/me` |
| Auth | Bearer token (Google OAuth access token) |
| Used in | `gmail.py` |

| Endpoint | Method | Purpose |
|---|---|---|
| `/messages` | GET | List message IDs in the inbox (max 30) |
| `/messages/{id}` | GET | Fetch full message content by ID |

**Example response snippet (messages list):**
```json
{
  "messages": [
    { "id": "18d4f2a3b9c1e5f7", "threadId": "18d4f2a3b9c1e5f7" },
    { "id": "18d4f2a3b9c1e000", "threadId": "18d4f2a3b9c1e000" }
  ]
}
```

---

#### Google OAuth API

| Endpoint | Purpose |
|---|---|
| `https://accounts.google.com/o/oauth2/v2/auth` | Redirects user to Google login |
| `https://oauth2.googleapis.com/token` | Exchanges auth code for access + refresh tokens |
| `https://www.googleapis.com/oauth2/v2/userinfo` | Fetches user's name, email, and profile picture |

---

#### Groq API (AI Classification)

| Detail | Value |
|---|---|
| Endpoint | `https://api.groq.com/openai/v1/chat/completions` |
| Model | `llama-3.3-70b-versatile` |
| Auth | Bearer token (Groq API key) |
| Used in | `ai.py` |

**Request body:**
```json
{
  "model": "llama-3.3-70b-versatile",
  "messages": [{ "role": "user", "content": "<classification prompt>" }],
  "temperature": 0.1,
  "max_tokens": 2000
}
```

**Response (parsed by the app):**
```json
[
  { "index": 0, "priority": "high", "category": "Work", "summary": "Interview scheduled for Monday at 10am." },
  { "index": 1, "priority": "low", "category": "Promotions", "summary": "Myntra sale offering 50% off this weekend." }
]
```

---

### Internal App Routes

| Route | Method | Auth Required | Description |
|---|---|---|---|
| `/` | GET | No | Landing page |
| `/auth/login` | GET | No | Redirects to Google login |
| `/auth/callback` | GET | No | Handles Google's OAuth callback |
| `/dashboard` | GET | Yes | Main email dashboard |
| `/email/{email_id}` | GET | Yes | Individual email detail |
| `/fetch-emails` | POST | Yes | Fetch new emails from Gmail |
| `/refresh-emails` | POST | Yes | Wipe and re-fetch all emails |
| `/filter` | GET | Yes | Filter emails by priority/category/read |
| `/search` | GET | Yes | Search emails by keyword |
| `/logout` | GET | Yes | Clear session and redirect to home |
| `/health` | GET | No | Health check endpoint |

---

## 🗄️ Database

**Database:** SQLite (`email_intelligence.db` — auto-created in the project root on first run)

**Why SQLite?** For a single-user or small-team tool, SQLite is ideal — zero installation, zero configuration, and the entire database is a single portable file.

---

### Table: `users`

Stores everyone who logs in via Google.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-incrementing primary key |
| `email` | TEXT (UNIQUE) | Google email address — one row per user |
| `name` | TEXT | Full name from Google profile |
| `picture` | TEXT | Profile picture URL |
| `access_token` | TEXT | Current Gmail API access token |
| `refresh_token` | TEXT | Long-lived token for renewing access |
| `created_at` | TEXT | When the user first logged in |
| `last_login` | TEXT | When the user most recently logged in |

---

### Table: `emails`

Stores all fetched and AI-classified emails.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-incrementing primary key |
| `gmail_id` | TEXT | Gmail's own unique message ID |
| `user_email` | TEXT | Which user this email belongs to |
| `subject` | TEXT | Email subject line |
| `sender` | TEXT | Display name of sender |
| `sender_email` | TEXT | Email address of sender |
| `snippet` | TEXT | Short preview (first ~100 characters) |
| `body` | TEXT | Full plain-text email body |
| `date` | TEXT | Date the email was received |
| `is_read` | INTEGER | 0 = unread, 1 = read |
| `priority` | TEXT | `high`, `medium`, or `low` (AI-assigned) |
| `category` | TEXT | `Work`, `Finance`, `Promotions`, etc. (AI-assigned) |
| `ai_summary` | TEXT | One-line AI-generated summary |
| `fetched_at` | TEXT | When NexInbox saved this email |

**Key Constraint:** `UNIQUE(gmail_id, user_email)` — prevents storing the same email twice for the same user, even if you click "Fetch" multiple times.

---

### Relationships
users.email (1) ──────────── (many) emails.user_email

Each user can have many emails. Each email belongs to exactly one user.

---

## 🤖 AI Engine

### Model

**Groq API** running **Meta's Llama 3.3 70B Versatile** model.

- **Why Groq?** Groq offers the fastest LLM inference available (often under 1 second per response), and has a generous free tier.
- **Why Llama 3.3 70B?** It has strong real-world instruction-following and language understanding, making it well-suited for nuanced classification tasks like distinguishing "hiring alert" (Work) from "OTP code" (Other).

---

### Prompt Design

The classification prompt in `ai.py` is carefully engineered with:

- **Strict label sets** — the model can only output `high/medium/low` and a fixed list of six categories
- **Explicit rules for edge cases** — e.g., `"Google Hiring Alert" → Work, medium` and `"Security alert from Google" → Other, high`
- **Low temperature (0.1)** — minimizes randomness; the model gives consistent, deterministic answers
- **JSON-only response** — the prompt explicitly instructs the model to return only a JSON array with no surrounding text

---

### Input

```json
[
  {
    "index": 0,
    "subject": "Your interview is scheduled for Monday",
    "sender": "hr@company.com",
    "preview": "Dear candidate, your technical interview..."
  }
]
```

### Output

```json
[
  {
    "index": 0,
    "priority": "high",
    "category": "Work",
    "summary": "Technical interview scheduled for Monday at 10am."
  }
]
```

---

### Fallback Classifier

If the Groq API is unavailable or returns an error, `ai.py` automatically falls back to a keyword-based classifier (`assign_defaults`) that uses word matching on subject, sender, and snippet to assign reasonable defaults for priority and category.

---

### Limitations

- Classification quality depends on the email snippet and subject — very short or vague emails may be miscategorised
- The model can occasionally misclassify ambiguous emails (e.g., a LinkedIn job post could be Work or Promotions)
- Groq's free tier has rate limits, handled by the 6-second delay between batches

---

### Evaluating Accuracy

Run the standalone evaluation tool:

```bash
python evaluate_ai.py
```

This loads your stored emails, lets you confirm or correct each AI label, then prints:
- Overall accuracy percentage
- Confusion matrix for priority and category
- Per-category accuracy breakdown

Use the results to identify where the prompt needs refinement.

---

## 🔒 Security

| Concern | How It's Handled |
|---|---|
| **Authentication** | Google OAuth 2.0 — no passwords ever stored |
| **Access tokens** | Stored in the database and session; never exposed in URLs |
| **Refresh tokens** | Stored securely in the database; used only for silent renewal |
| **Session security** | Signed cookies via Starlette SessionMiddleware using `SECRET_KEY` |
| **Secret management** | All credentials in `.env` file, excluded from Git via `.gitignore` |
| **User isolation** | Every database query is scoped to `user_email` — users cannot access each other's emails |
| **Gmail access** | Read-only scope (`gmail.readonly`) — the app cannot send, delete, or modify any email |
| **Expired tokens** | Any 401 response from Gmail triggers a session clear and redirect to login |

> ⚠️ **Important:** Before deploying to production, set `https_only=True` in SessionMiddleware and use a proper secret key (at least 32 random characters).

---

## ⚡ Performance

| Optimization | Detail |
|---|---|
| **Batch AI requests** | Emails are sent to Groq in batches of 10 rather than one at a time, reducing total API calls |
| **Deduplication before fetch** | Existing Gmail IDs are loaded once before fetching, so duplicate emails are skipped before parsing — not after |
| **Bulk DB insert** | All new emails are saved in a single transaction via `save_emails_bulk`, not in a loop of individual inserts |
| **WAL mode** | SQLite is configured with `PRAGMA journal_mode=WAL` for better concurrent read/write performance |
| **Rate-limit awareness** | A 6-second delay between Groq batches prevents hitting API rate limits, avoiding costly retries |
| **Incremental fetch** | On re-visits, only emails not already in the database are fetched and classified |

---

## 🛡️ Error Handling

| Failure Scenario | How It's Handled |
|---|---|
| User denies Google login | Redirected to `/?error=login_denied` |
| Token exchange fails | Redirected to `/?error=token_failed` |
| Gmail API returns 401 (token expired) | Session cleared, redirected to `/auth/login` |
| Gmail API returns other error | Returns `{"count": 0, "error": "api_error"}` gracefully |
| Groq API returns non-200 | Falls back to keyword-based `assign_defaults` for that batch |
| Groq returns malformed JSON | Caught by `json.JSONDecodeError`, falls back to defaults |
| Email parse error | Individual email is skipped with a warning; others continue |
| Database save error | Rolled back with error logged; app continues |
| Email not found (detail page) | Returns HTTP 404 |
| No emails in DB for user | Dashboard renders with zeroed stats; no crash |

---

## 🔮 Future Improvements

- [ ] **Multi-account support** — connect and switch between multiple Gmail accounts
- [ ] **AI reply drafting** — one-click AI-generated reply suggestions for each email
- [ ] **Push notifications** — browser or desktop alerts for new high-priority emails
- [ ] **Calendar integration** — detect meeting invitations and add to Google Calendar automatically
- [ ] **Unsubscribe automation** — detect and unsubscribe from mailing lists in one click
- [ ] **Email threading** — group emails by conversation thread instead of individual messages
- [ ] **Vector search** — semantic search using embeddings instead of keyword LIKE queries
- [ ] **Custom priority rules** — let users define their own classification rules
- [ ] **Export to CSV** — download classified inbox as a spreadsheet
- [ ] **Dark/light mode toggle** — user-controlled theme preference
- [ ] **PostgreSQL migration** — replace SQLite with PostgreSQL for multi-instance deployments
- [ ] **Deployment to cloud** — one-click deploy to Railway, Render, or Fly.io

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/yourusername/nexinbox.git
cd nexinbox

# 3. Create a new branch for your feature
git checkout -b feature/your-feature-name

# 4. Make your changes

# 5. Commit with a clear message
git commit -m "feat: add email threading support"

# 6. Push to your fork
git push origin feature/your-feature-name

# 7. Open a Pull Request on GitHub
```

### Contribution Guidelines

- Follow the existing code style and file structure
- Add comments explaining non-obvious logic
- Test your changes before submitting a PR
- One feature or fix per PR — keep it focused
- Update this README if your change affects setup or usage

### Commit Message Format
feat: add new feature
fix: resolve a bug
docs: update documentation
refactor: restructure code without changing behaviour
test: add or update tests

---

## 📄 License

This project is licensed under the **MIT License** — you are free to use, modify, and distribute it for personal or commercial purposes.

See the [LICENSE](LICENSE) file for full details.

---

## 👤 Author

**[Your Name]**

- 🎓 Intern at NALCO, Corporate Bhawan
- 💼 [LinkedIn](https://linkedin.com/in/yourprofile)
- 🐙 [GitHub](https://github.com/yourusername)
- 📧 [your.email@gmail.com](mailto:your.email@gmail.com)

---

## 🙏 Acknowledgements

- [**Groq**](https://groq.com) — For providing ultra-fast LLM inference via their free API tier
- [**Meta AI**](https://ai.meta.com) — For the open-weight Llama 3.3 70B model
- [**Google**](https://developers.google.com) — For the Gmail API and OAuth 2.0 platform
- [**FastAPI**](https://fastapi.tiangolo.com) — For an exceptional Python web framework
- [**Sebastián Ramírez**](https://github.com/tiangolo) — Creator of FastAPI
- [**Starlette**](https://www.starlette.io) — For the ASGI toolkit underlying FastAPI
- [**NALCO, Corporate Bhawan**](https://nalcoindia.com) — For providing the internship opportunity and project environment

---

<div align="center">

Built with ❤️ during an internship at NALCO, Corporate Bhawan

⭐ If this project helped you, consider giving it a star on GitHub!

</div>