<h1 align="center">✉️ NexInbox</h1>
<p align="center"><b>Your Gmail inbox, but an AI has already read it and told you what actually matters.</b></p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/Database-PostgreSQL%20(Supabase)-3ECF8E?logo=supabase&logoColor=white"></a>
  <a href="https://groq.com/"><img src="https://img.shields.io/badge/LLM-Groq%20%7C%20gpt--oss--120b-orange"></a>
  <a href=".github/workflows/ci.yml"><img src="https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white"></a>
  <a href="https://nexinbox.onrender.com"><img src="https://img.shields.io/badge/Live-nexinbox.onrender.com-46E3B7?logo=render&logoColor=white"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green"></a>
</p>

<p align="center"><b><a href="https://nexinbox.onrender.com">🔗 Live Demo</a></b> · <a href="#-what-is-this-really">What Is This?</a> · <a href="#️-architecture">Architecture</a> · <a href="#️-installation">Setup</a> · <a href="#-real-world-scenarios">Real-World Scenarios</a> · <a href="#-honest-limitations">Limitations</a></p>

---

> 💡 **New here, and don't know what OAuth, an LLM, or a database is?** That's exactly who this README is written for. Every technical section below has a 🟢 **plain-English** explanation before the 🔵 **technical** one. Just read top to bottom.

<!--
🖼️ ADD BANNER SCREENSHOT HERE (top of README)
What to add: A full-width screenshot of the populated dashboard — sidebar
with filters, priority badges (🔴🟡🟢) and colored category tags visible
in the email list, stats counters at the top.
Where: Right below this comment, before the Table of Contents.
Filename: docs/images/banner.png
Purpose: The first thing anyone sees. Should say "this is a real, working
product" before they've read a single word.
-->

## 📖 Table of Contents

- [What Is This, Really?](#-what-is-this-really)
- [The Problem It Solves](#-the-problem-it-solves)
- [Who It's For](#-who-its-for)
- [Features](#-features)
- [Demo](#-demo)
- [Architecture](#️-architecture)
- [Tech Stack, Explained From Scratch](#-tech-stack-explained-from-scratch)
- [Project Structure](#️-project-structure)
- [How It Works — The Complete Flow](#-how-it-works--the-complete-flow)
- [Installation](#️-installation)
- [Configuration](#-configuration)
- [How to Use It](#-how-to-use-it)
- [Real-World Scenarios (Read This)](#-real-world-scenarios)
- [What's Remembered, and For How Long](#-whats-remembered-and-for-how-long)
- [Capability Matrix](#-capability-matrix)
- [What This App CAN / CANNOT Do](#-what-this-app-can-do)
- [Edge Cases](#️-edge-cases)
- [Testing](#-testing)
- [AI Accuracy — How Would You Even Check?](#-ai-accuracy--how-would-you-even-check)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Deployment](#️-deployment)
- [Security](#-security)
- [Performance & Scalability](#-performance--scalability)
- [Honest Limitations](#-honest-limitations)
- [Future Improvements / Roadmap](#-future-improvements--roadmap)
- [What This Project Demonstrates](#-what-this-project-demonstrates)
- [Placement / Interview Preparation](#-placement--interview-preparation)
- [Resume Description](#-resume-description)
- [Challenges Faced](#-challenges-faced)
- [Key Learnings](#-key-learnings)
- [FAQ](#-faq)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## 📖 What Is This, Really?

Picture your Gmail inbox right now. Somewhere in there is an interview call you actually need to see today, buried under twelve promotional emails from Myntra and a LinkedIn notification about "14 people viewed your profile."

**NexInbox is a program that opens your inbox for you, reads every email, and quietly sorts them** — this one's urgent, this one can wait, this one's just a sale — before you even look at it. Instead of a plain list of subject lines, you get a dashboard where the important stuff is already flagged 🔴, the maybe-later stuff is 🟡, and the stuff that genuinely doesn't matter is 🟢.

It does this using an actual AI (a large language model), not a hardcoded list of rules — though there's a rules-based backup in case the AI is unreachable, explained in [Scenario 4](#scenario-4--the-ai-service-is-down-or-your-groq-key-is-missing).

## 🎯 The Problem It Solves

Manually triaging a busy inbox is slow and error-prone — it's easy to skim past something important while scrolling through a dozen things that don't matter. NexInbox does that triage automatically every time you fetch new mail, so the sorting is already done before you open your inbox.

## 👤 Who It's For

- Students and job-seekers whose inbox mixes interview calls with newsletters and promo spam
- Anyone who checks their inbox multiple times a day and wants a faster first pass
- Developers who want a compact, real example of OAuth 2.0 + an LLM API + PostgreSQL wired together properly in FastAPI

---

## ✨ Features

| | Feature | What it actually does |
|---|---|---|
| 🔐 | **Google Sign-In** | Real OAuth 2.0 login with CSRF `state` protection — NexInbox never sees your password |
| 📥 | **Inbox Fetching** | Pulls your latest 30 inbox emails on demand |
| 🤖 | **AI Classification** | Every email gets a priority (🔴 high / 🟡 medium / 🟢 low), a category, and a 1-sentence summary — via LLM (Groq), or keyword rules if the AI is unavailable |
| 🛟 | **Never Leaves You Blank** | If the AI is down, a keyword-based backup classifier still tags every email |
| 🔍 | **Search** | Matches subject, sender name, sender email, snippet, or AI summary text |
| 🧭 | **One-Click Filters** | Jump to High Priority, Unread, Work, Finance, etc. |
| 📊 | **Live Stats** | Total, unread, and a breakdown by priority/category, computed fresh from the database |
| ✅ | **Real Read-Status** | Reflects what's actually unread in your real Gmail, at fetch time |
| 🔄 | **Two Kinds of Refresh** | "Fetch" grabs only new mail; "Refresh" atomically wipes and re-checks everything |
| 📄 | **Full Email View** | Full body + AI summary in one card |

---

## 🎥 Demo

<!--
🖼️ ADD DEMO GIF HERE
What to add: login → dashboard → click "Fetch Emails" → list populates
with badges/tags → open one email → show the AI summary card.
Where: Right below this comment.
Filename: docs/images/demo.gif
Purpose: Single highest-impact visual in this README.
-->

---

## 🏗️ Architecture

🟢 **Plain English:** your browser talks to a Python server (FastAPI). That server talks to three outside services on your behalf — Google (login + mail), Groq (AI classification), and a database (memory). Nothing outside ever talks to your browser directly.

┌──────────────┐ ┌────────────────────┐ ┌──────────────────────┐
│ Browser │ ───► │ FastAPI (main.py) │ ───► │ Jinja2 Templates │
│ (what you │ ◄─── │ + login session │ ◄─── │ dashboard / email / │
│ actually see)│ └─────────┬───────────┘ │ index .html │
└──────────────┘ │ └──────────────────────┘
┌──────────────┼───────────────┐
▼ ▼ ▼
┌───────────┐ ┌────────────┐ ┌───────────────┐
│ auth.py │ │ gmail.py │ │ ai.py │
│ "log me │ │ "get my │ │ "sort my │
│ in with │ │ emails" │ │ emails" │
│ Google" │ │ │ │ │
└─────┬──────┘ └──────┬─────┘ └───────┬─────────┘
│ │ │
└────────────────┼────────────────┘
▼
┌─────────────────┐
│ database.py │
│ "remember │
│ everything" │
│ PostgreSQL/Supabase│
└─────────────────┘


<!--
🖼️ ADD A POLISHED ARCHITECTURE DIAGRAM HERE (optional)
What to add: A cleaner redraw of the diagram above (e.g. in Excalidraw).
Where: Right below this comment.
Filename: docs/images/architecture.png
Purpose: Reads faster than ASCII for a skimming recruiter.
-->

---

## 🧠 Tech Stack, Explained From Scratch

| Technology | 🟢 Plain English | 🔵 How NexInbox Actually Uses It |
|---|---|---|
| **FastAPI** | A tool for building a website's "backend" — decides what happens when you click a button | Every route (`/dashboard`, `/fetch-emails`, `/search`, etc.) lives in `main.py`. It's `async`, so one slow request doesn't freeze everyone else. |
| **OAuth 2.0 (Google Sign-In)** | A safe way to let an app use your Google account without ever handing over your password | Implemented by hand with `httpx` (no Google SDK) — the standard "authorization code" flow, with a CSRF `state` parameter verified on callback. Requests only the `gmail.readonly` scope. |
| **Gmail API** | The official way for an app to fetch your emails, once you've said yes | REST calls to `gmail.googleapis.com` — a list of message IDs, then each message's full content. |
| **LLM via Groq** | An AI that reads text and answers questions about it, the same idea behind ChatGPT | Batches of up to 10 emails sent to Groq's API (model: `openai/gpt-oss-120b`), with a strict prompt requiring JSON back, validated before being trusted. |
| **PostgreSQL (Supabase)** | A database — an organized, permanent notebook the app writes to and reads from | Two tables (`users`, `emails`) via a connection pool. Chosen because Render's filesystem is wiped on every restart — the original SQLite version lost data constantly. |
| **Session Cookie** | A small note the browser keeps so the site remembers you're logged in | Signed but **not encrypted** — holds only your name/email/photo, never your Gmail token. The token lives only in Postgres. |
| **Jinja2** | Fills an HTML page with real data before sending it to your browser | `index.html`, `dashboard.html`, `email_detail.html` rendered server-side — no separate JS frontend. |
| **pytest + GitHub Actions** | Automated checks that run every time code changes | CI verifies every core file imports cleanly, then runs the test suite — both must pass. |

---

## 🗂️ Project Structure

```text
email_intelligence/
│
├── main.py                   # ⭐ Entry point — every HTTP route
├── auth.py                   # ⭐ Google login: redirect, callback, token refresh
├── gmail.py                  # ⭐ Gmail API calls + email parsing
├── ai.py                     # ⭐ Groq classification + keyword fallback
├── database.py               # ⭐ All PostgreSQL reads/writes, connection pooling
│
├── evaluate_ai.py            # 🧪 Manual CLI tool to score AI accuracy
├── test_basic.py             # 🧪 Automated tests for gmail.py's parsing functions
│
├── templates/
│   ├── index.html            # Landing page — "Login with Google"
│   ├── dashboard.html        # Main inbox view
│   └── email_detail.html     # Full email + AI summary view
│
├── static/css/
│   ├── .gitkeep              # Empty placeholder — keeps this folder tracked in git even before base.css existed
│   └── base.css              # One shared stylesheet
│
├── .github/workflows/
│   └── ci.yml                # Runs tests automatically on every push
│
├── requirements.txt
├── Procfile                  # Tells Render how to start the app
├── .gitignore
└── LICENSE
```

## How the files talk to each other

The browser directly reaches two files' routes:

- `main.py` — all the main pages: dashboard, email detail, fetch, search, etc.
- `auth.py` — the `/auth/login` and `/auth/callback` steps of the Google login flow, mounted as their own router.

`main.py` then calls into `gmail.py` and `ai.py` internally when you click **"Fetch Emails"**, and into `database.py` for everything that needs remembering.

`gmail.py` does declare its own router too, but it has no actual routes defined on it — it's mounted but currently unused by the browser.

`evaluate_ai.py` is a separate script run manually in a terminal — not part of the running website at all.

---

## 🔄 How It Works — The Complete Flow

```
You click "Login with Google"
        ↓
Google shows its own consent screen — you approve read access
        ↓
Google redirects back with a temporary code
        ↓
NexInbox verifies the CSRF state, trades the code for a real access token
        ↓
Token saved in the database — never in your browser
        ↓
You land on the dashboard — empty, until your first fetch
        ↓
You click "Fetch Emails"
        ↓
NexInbox asks Gmail for your latest 30 inbox messages
        ↓
Already-stored emails are skipped — only new ones processed
        ↓
Each new email is parsed: subject, sender, date, body, real read status
        ↓
Emails sent to the AI in batches of 10
        ↓
AI replies with priority + category + summary for each (or keyword fallback if it fails)
        ↓
Everything saved to the database
        ↓
Dashboard reloads with your color-coded, filterable inbox
```

---

## ⚙️ Installation

1. Install Python 3.12: `python --version`
2. Clone the repo: `git clone https://github.com/Subham093/nexinbox.git && cd nexinbox`
3. Create a virtual environment: `python -m venv venv`
4. Activate it — Windows (PowerShell): `venv\Scripts\Activate.ps1` (if this fails with a permissions error, run 
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` 
first, then try again) 
 .Windows (cmd): `venv\Scripts\activate.bat` 
 · Mac/Linux: `source venv/bin/activate`
5. Install packages: `pip install -r requirements.txt`
6. Set up a Google Cloud project with OAuth credentials + the Gmail API enabled
7. Get a free Groq API key at [console.groq.com](https://console.groq.com)
8. Set up a PostgreSQL database (the live version uses [Supabase](https://supabase.com))
9. Create a `.env` file (see Configuration below)
10. Run it: `python main.py` → open `http://localhost:8000`

## 🔐 Configuration

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
REDIRECT_URI=http://localhost:8000/auth/callback   # must exactly match the redirect URI registered in Google Cloud Console

GROQ_API_KEY=your_groq_api_key        # optional — app still runs without it, using keyword-based classification instead of the LLM
GROQ_MODEL=openai/gpt-oss-120b        # optional — already the default

DATABASE_URL=postgresql://user:password@host:5432/dbname
DB_POOL_MAX=10                        # optional — default is 10

SECRET_KEY=a_long_random_string       # required in production
ENVIRONMENT=development               # set to "production" when deploying
```

🟢 An environment variable is a setting kept outside your code — for secrets like API keys, it's how you keep them off GitHub; for everything else, it's just a convenient place to configure the app without editing code.

> ⚠️ If `SECRET_KEY` is missing, the app runs with an insecure placeholder — but **only** while `ENVIRONMENT` isn't `production`. In production, it refuses to start rather than run with a guessable key.

---

## 🧑‍💻 How to Use It

1. Open the app, click **Login with Google**, approve the consent screen
2. Click **Fetch Emails** — your first sync
3. Browse the dashboard: priority badges, category tags, live stats
4. Use the sidebar to jump to High Priority, Unread, Work, Finance, etc.
5. Use search for a specific email
6. Click any email to read the full body + AI summary — this marks it read inside NexInbox
7. From then on, the button relabels itself **"Check New Emails"** for grabbing just what's new, or use **"Full Refresh"** to wipe and fully re-classify everything from scratch

---

## 🧭 Real-World Scenarios

### Scenario 1 — First Login and First Fetch

<!--
🖼️ ADD SCREENSHOT HERE: index.html landing page
Where: Right below this heading. Filename: docs/images/login-page.png
-->

You log in, land on an empty dashboard, click **Fetch Emails**. NexInbox pulls your latest 30 inbox messages and classifies all of them, since none exist yet.

<!--
🖼️ ADD SCREENSHOT HERE: populated dashboard right after first fetch
Filename: docs/images/first-fetch.png
-->

### Scenario 2 — Clicking "Check New Emails" Later

✅ **Fully supported, and cheap.** NexInbox already knows every `gmail_id` it has stored. Only genuinely new emails get processed:

```python
if skip_existing and msg_id in existing_ids:
    skipped += 1
    continue
```

Nothing new? You'll see "Inbox up to date" — no wasted AI calls, no duplicate rows.

### Scenario 3 — Clicking "Full Refresh" Instead

⚠️ **A different operation, not a stronger "Fetch."** Refresh deletes **all** stored emails and re-fetches + re-classifies everything, atomically:

```python
cursor.execute("DELETE FROM emails WHERE user_email = %s", (user_email,))
# ...then every fetched email is re-inserted
conn.commit()   # only commits if every step succeeded
```

If anything fails partway, the whole thing rolls back and your old data is kept — you're never left with a half-wiped inbox.

**Important overlap gap:** both "Fetch" and "Refresh" request the exact same latest-30-message window from Gmail. If more than 30 new emails arrive between checks, the oldest of that overflow is **never fetched by either action** — Refresh does not mean "catch up on everything since my last visit."

### Scenario 4 — The AI Service Is Down or Your Groq Key Is Missing

🛟 **Nothing breaks — the dashboard just gets less smart for that batch.** `assign_defaults()` kicks in with keyword matching instead:

```python
if not GROQ_API_KEY:
    print("⚠️  No GROQ_API_KEY found — using default values")
    return assign_defaults(emails)
```

Every email still gets a priority and category — just a cruder one. **There is currently no visual difference in the dashboard** between an AI-classified email and a fallback-classified one — a known, documented gap.

### Scenario 5 — Opening an Email

Marks it read **inside NexInbox's own database** immediately. This does **not** reach out and mark it read in your actual Gmail — the two "read" states are tracked completely separately after that point, and the relationship never runs the other direction either (reading in Gmail is only reflected here at your *next* fetch).

### Scenario 6 — Your Google Access Token Expires *(checked only when you next click Fetch/Refresh)*

Handled silently — NexInbox tries your stored refresh token to get a new access token automatically. Only if that also fails are you redirected to log in again.

---

## 🧠 What's Remembered, and For How Long

| What | Remembered? | Where / How Long |
|---|---|---|
| That you're logged in | ✅ | Session cookie, 24 hours or until logout |
| Gmail access/refresh tokens | ✅ | PostgreSQL only — **never** in your browser cookie |
| Every fetched email | ✅ | PostgreSQL, permanently — there's currently no feature to manually delete an email; only a "Full Refresh" replaces stored data |
| Read/unread status | ✅ | PostgreSQL — independent from Gmail's own status, set automatically at fetch time and updated when you open an email |
| New emails arriving in Gmail | ❌ (until you click Fetch) | No automatic sync |
| Anything beyond your latest 30 emails at fetch time | ❌ | Older mail simply never pulled in |
| Emails beyond the newest 50 (already stored) | ⚠️ Stored, but not visible | Still counted in your total stats, but dashboard/search/filter all cap at the newest 50 — no pagination to reach older stored ones |
| Your search/filter selection after leaving the page | ❌ | Just URL parameters — refresh resets to "All" |

---

## 🚦 Capability Matrix

| Capability | Supported? | Actual Behavior | Limitations |
|---|---|---|---|
| Google Sign-In | ✅ | Real OAuth 2.0 with CSRF `state` verification | Session cookie signed, not encrypted |
| Fetch inbox emails | ✅ | Latest 30 messages from `INBOX` label | No pagination; overflow beyond 30 is lost |
| AI priority/category/summary | ✅ | Real Groq LLM call, output validated against a fixed allow-list | Can misclassify; no confidence score shown |
| Fallback when AI unavailable | ✅ | Deterministic keyword classifier | ⚠️ Silent — no UI indicator this happened |
| Search | ✅ | Matches subject, sender name, sender email, snippet, or AI summary text | Capped at 50 results |
| Filter by priority/category/read status | ✅ | Shareable URLs (e.g. `/filter?priority=high`) | Invalid values silently ignored, not erred |
| Real Gmail read/unread sync | ⚠️ Partial | Reflects Gmail's real state, but only as a **snapshot at fetch time** | Not live; one-directional (Gmail → NexInbox only) |
| Incremental fetch | ✅ | Skips already-stored emails | — |
| Full resync (Refresh) | ✅ | Atomic wipe + re-fetch + re-classify | Shares the same 30-message cap as Fetch |
| CSRF protection on state-changing forms | ⚠️ Partial | Login has explicit CSRF `state`; Fetch/Refresh forms rely only on `same_site=lax` cookie behavior | No dedicated per-form CSRF token |
| Token encryption at rest | ❌ | Tokens stored as plain text in Postgres | Real, documented security gap |
| Automated tests | ⚠️ Partial | Only `gmail.py`'s pure parsing functions covered | Auth, AI, database, and routes are untested |
| Manual AI accuracy check | ⚠️ Partial | `evaluate_ai.py` works, but is an interactive CLI, not automatic | Not run automatically, no fixed benchmark number |
| Reply / compose / send email | ❌ | Not supported | Read-only scope by design |
| Archive / label / delete in real Gmail | ❌ | Not supported | NexInbox never writes back to Gmail |
| Multiple inboxes per account | ❌ | Not supported | One Gmail account per login |
| Real-time updates | ❌ | Not supported | Manual click-to-fetch only |
| Scheduled auto-refresh | 🔄 Future | Not implemented | Would need a scheduler or Gmail push notifications |

---

## ✅ What This App CAN Do

- Log you in securely with your real Google account
- Pull your latest 30 inbox emails on demand
- Classify every one with AI — priority, category, 1-sentence summary
- Keep working (with a cruder fallback) even if Groq is unreachable
- Let you search and filter without reopening Gmail
- Show you what's genuinely unread in your real inbox, as of your last fetch

## ❌ What This App CANNOT Do

- Send, reply to, forward, archive, label, or delete anything in real Gmail
- Show more than ~30–50 emails at a time, with no pagination
- Automatically check for new mail without a manual click
- Guarantee the AI never misclassifies something
- Support more than one Google account per session
- Visually distinguish an AI-classified email from a keyword-fallback one
- Encrypt your stored Gmail tokens

---

## ⚠️ Edge Cases

| Situation | What Actually Happens |
|---|---|
| No `GROQ_API_KEY` set | Every email classified via keyword fallback |
| Groq returns malformed JSON | That batch falls back to keywords; other batches unaffected |
| Groq rate-limits you (`429`) | Automatic retry with exponential backoff, up to 2 extra attempts |
| Gmail rate-limits you (`429`) | One retry after a short pause |
| Access token expires mid-session | Silent automatic refresh; falls through to re-login only if that also fails |
| OAuth `state` mismatch on callback | Rejected outright as possible CSRF — error redirect, no login granted |
| You deny the Google consent screen | Clear "login denied" redirect, no crash |
| One Gmail message fails to parse | That message is skipped; the rest of the batch still processes |
| Database briefly unreachable | Dashboard/filter/search show an empty state; Fetch/Refresh redirect to login; opening a specific email shows a misleading "Email not found" (404) instead of a raw crash |
| More than 30 new emails since last check | Oldest of the overflow is never fetched, by either Fetch or Refresh |
| "Full Refresh" fails partway through | Old data is kept untouched — never a wiped, half-empty inbox |

---

## 🧪 Testing

```bash
pytest -v
```

🟢 **What this means:** automated checks that run real functions and confirm they return the right answer — no manual clicking required to verify these specific pieces.

**What's actually covered:** the pure, no-network functions in `gmail.py` — sender name/email extraction, HTML-entity cleanup, and email date parsing (9 tests total).

**Honestly not covered:** the OAuth login flow, live Gmail API calls, the AI classification logic, the database layer, and every HTTP route. All depend on external services or a live database and would need mocking to test properly — a real, acknowledged gap.

---

## 📊 AI Accuracy — How Would You Even Check?

Run `python evaluate_ai.py` after fetching real emails. It pulls your classified emails, shows what the AI decided for each, lets you confirm or correct it, then prints an overall accuracy percentage, a confusion matrix, and a per-category accuracy breakdown.

This is a **manual, interactive developer tool** — no fixed accuracy number is claimed here, because it depends entirely on your own inbox's contents at the time you run it.

---

## 🔄 CI/CD Pipeline

✅ **Real CI exists**, via GitHub Actions (`.github/workflows/ci.yml`), on every push to `main`:

Developer → Git Push → GitHub Actions
→ Install dependencies
→ Verify every core module imports cleanly (ai, gmail, auth, database, main)
→ Run the full pytest suite
→ ❌ fail = red, blocks confidence in the deploy
→ ✅ pass = green
(separately) Render auto-deploys from the same push


**Honest distinction:** this is genuine CI (real, enforced checks), but there's **no CD gate** — Render's auto-deploy and GitHub Actions currently run independently on the same push, rather than the deploy waiting on a green CI result first.

---

## ☁️ Deployment

NexInbox is live at **[nexinbox.onrender.com](https://nexinbox.onrender.com)**, deployed on **[Render](https://render.com)**:

- Start command (`Procfile`): `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
- Database: PostgreSQL hosted on **Supabase**, chosen because Render's filesystem doesn't persist across restarts
- All environment variables from Configuration set in Render's dashboard, with `ENVIRONMENT=production`

**Free-tier characteristic:** the instance spins down after inactivity; the first request afterward can take 50+ seconds while it wakes up — a hosting-platform behavior, not an app bug.

---

## 🔒 Security

- **CSRF-protected login** — a random `state` value checked on every OAuth callback
- **Your Gmail token never touches your browser** — stored only in PostgreSQL
- **Session cookie is signed but not encrypted** — deliberately holds only non-sensitive identity fields
- **Production refuses to start without a real `SECRET_KEY`**
- **Prompt-injection aware** — email content is attacker-influenceable data, treated as pure data, never as instructions; AI output is checked against a fixed allow-list before use
- **All database queries are parameterized** — no raw string concatenation into SQL
- **`.env` and local database files are git-ignored**
- ⚠️ **Known gap:** Gmail tokens are stored as **plain text** in Postgres — not encrypted at rest
- ⚠️ **Known gap:** no dedicated CSRF token on the Fetch/Refresh POST forms — partially mitigated by `same_site=lax`, not equivalent to the login flow's protection

---

## ⚡ Performance & Scalability

- AI calls batched (10 emails at a time) with a 6-second pause between batches, plus automatic retries
- Gmail calls retry once on rate-limiting
- Database connections pooled rather than opened fresh per request
- No background job queue or caching layer — comfortably handles one person fetching 30 emails at a time; **not built or tested for high-concurrency, many-users-at-once use**

---

## 🚧 Honest Limitations

- Only your latest 30 emails are ever fetched, and only 50 shown/searched at once — a recent-activity dashboard, not a full mailbox archive
- Test coverage is thin — real functionality (AI, OAuth, database) isn't covered by automated tests, only plain parsing helpers are
- No write access to Gmail at all
- AI can misclassify, with no visual indicator distinguishing AI vs. fallback decisions
- No scheduling — fetching is always manual
- Single Gmail account per login session — no switching between multiple inboxes without logging out and back in (though the database itself is multi-tenant: different users' data is fully isolated by email)
- Gmail tokens stored unencrypted

---

## 🔮 Future Improvements / Roadmap

> Nothing below exists yet — honest ideas for what's next, not current features.

**Near-term**
- [ ] Visible UI indicator when AI classification falls back to keyword rules
- [ ] CSRF token on the Fetch/Refresh POST forms

**Mid-term**
- [ ] Encrypt Gmail tokens at rest, with a real key-management approach
- [ ] Pagination beyond the current 30-fetch / 50-display caps
- [ ] Merge in automated test coverage for `auth.py`, `ai.py`, and `database.py` — already built and verified (mocked connection pool, transaction rollback tests, OAuth token-refresh tests) but not currently included in this version of the repo

**Long-term**
- [ ] Scheduled auto-refresh (cron or Gmail push notifications) instead of manual clicking
- [ ] Gate Render's auto-deploy on CI passing, instead of running independently
- [ ] Support for more than one connected Gmail account

---

## 🧠 What This Project Demonstrates

A hand-implemented OAuth 2.0 authorization-code flow (not a wrapper library) with CSRF protection and token refresh; real third-party API integration across two providers, with genuine exponential backoff on the Groq calls and simple retry-on-rate-limit for Gmail; prompt design with output validation rather than blind trust in an LLM's response; a deliberate fallback path for external AI failure; PostgreSQL schema design with pooling and atomic transactions; and a documented, deliberate trade-off around session cookie security.

---

## 🧗 Challenges Faced

- **Data loss risk on failed refreshes** — an early version of "Full Refresh" deleted existing emails before confirming the new fetch succeeded. Fixed by restructuring to fetch-then-replace atomically in one transaction.
- **Silent database bugs** — a schema migration (real `BOOLEAN`/`TIMESTAMP` columns) didn't retroactively apply to the already-deployed database, silently showing incorrect stats until diagnosed via terminal error logs.
- **Ephemeral hosting filesystem** — SQLite was the original database choice, but Render wipes its filesystem on every restart and redeploy — meaning any SQLite data would not persist. This was the actual reason for migrating to PostgreSQL on Supabase before this became a real problem in production.

## 💡 Key Learnings

- OAuth 2.0 is easy to *use* via a library, but implementing token exchange, CSRF state, and refresh by hand surfaces real security considerations easy to skip with an SDK
- A working fallback path is often more valuable in an interview conversation than the primary AI feature itself — it demonstrates thinking about failure, not just the happy path
- Schema migrations on an already-deployed database need explicit `ALTER TABLE` statements — `CREATE TABLE IF NOT EXISTS` silently does nothing on existing tables

---

## ❓ FAQ

<details>
<summary><b>Does NexInbox ever send, delete, or archive my real emails?</b></summary>
<br>
No. Read-only scope — nothing writes back to real Gmail.
</details>

<details>
<summary><b>Is my Gmail password stored anywhere?</b></summary>
<br>
No — Google handles login itself; NexInbox only ever receives a limited access token after you approve it.
</details>

<details>
<summary><b>If I mark an email read in NexInbox, does it mark it read in real Gmail?</b></summary>
<br>
No — one-directional. Reading in real Gmail eventually reflects here at your next fetch; the reverse never happens.
</details>

<details>
<summary><b>What happens if the AI gets something wrong?</b></summary>
<br>
It's classified incorrectly for that email — there's no way to manually correct a single email's label from the dashboard today. Running "Refresh" re-classifies everything, which may or may not change the result.
</details>

<details>
<summary><b>Why does clicking "Fetch Emails" twice sometimes do nothing?</b></summary>
<br>
Working as intended — if no new mail arrived since your last fetch, there's nothing new to process.
</details>

<details>
<summary><b>Can I connect more than one Gmail account?</b></summary>
<br>
Not currently — one Google account per login session.
</details>

---

## 🤝 Contributing

This is currently a personal portfolio project and not actively seeking contributions, but suggestions and issues are welcome via GitHub.

## 📜 License

This project is licensed under the [MIT License](./LICENSE).

## 👤 Author

**Subham Maheswari Jena**

Built as part of an internship project (NALCO) and a placement-interview portfolio, exploring OAuth 2.0, LLM API integration, and PostgreSQL-backed full-stack development with FastAPI.