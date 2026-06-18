# 📧 Email Intelligence System

An AI-powered email management dashboard that connects to your Gmail inbox, automatically classifies emails by priority, categorizes them, and generates smart summaries — all in a beautiful dark UI.

![Dashboard Preview](https://img.shields.io/badge/Status-Live-34d399?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.12-4f8ef7?style=flat-square) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-a78bfa?style=flat-square)

---

## ✨ Features

- **Google OAuth 2.0** — Secure login with your Gmail account
- **Real Gmail Integration** — Fetches your latest 30 inbox emails via Gmail API
- **AI Priority Classification** — Every email tagged as High 🔴 / Medium 🟡 / Low 🟢
- **Smart Categorization** — Work, Finance, Promotions, Social, Newsletters
- **AI Summaries** — 1-sentence summary for every email powered by Llama 3
- **Live Dashboard** — Stats cards showing total, unread, read, and priority counts
- **Sidebar Filters** — Filter by priority, category, or read status instantly
- **Search** — Search emails by sender, subject, or content
- **Smart Fetch** — Only downloads new emails, never duplicates
- **Multi-user** — Each user sees only their own emails

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Frontend | Jinja2 + HTML + CSS |
| Database | SQLite |
| Auth | Google OAuth 2.0 |
| Email API | Gmail API |
| AI Engine | Groq API (Llama 3.3 70B) |
| Sessions | Starlette SessionMiddleware |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/email-intelligence.git
cd email-intelligence
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install fastapi uvicorn[standard] python-dotenv jinja2 starlette \
  itsdangerous google-auth google-auth-oauthlib google-api-python-client \
  anthropic httpx aiohttp
```

### 4. Set up Google Cloud Console
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project
3. Enable **Gmail API**
4. Create **OAuth 2.0 credentials** (Web application)
5. Add `http://localhost:8000/auth/callback` as redirect URI
6. Add your Gmail as a test user

### 5. Get Groq API Key
1. Sign up at [console.groq.com](https://console.groq.com) (free)
2. Create an API key

### 6. Configure environment
Create a `.env` file in the project root:
```env
SECRET_KEY=your-random-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret
ANTHROPIC_API_KEY=will-add-later
GROQ_API_KEY=gsk_your-groq-key
```

### 7. Run the app
```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` 🎉

---

## 📁 Project Structure

```
email_intelligence/
├── main.py          # FastAPI app, all routes
├── auth.py          # Google OAuth 2.0 flow
├── gmail.py         # Gmail API integration
├── ai.py            # Groq AI analysis (priority + category + summary)
├── database.py      # SQLite database functions
├── .env             # Secret keys (never commit this!)
├── templates/
│   ├── index.html        # Landing page
│   ├── dashboard.html    # Main email dashboard
│   └── email_detail.html # Single email view
└── static/
    └── css/              # Additional stylesheets
```

---

## 🧠 How It Works

```
User Login (Google OAuth)
        ↓
Fetch 30 emails from Gmail API
        ↓
Parse each email (subject, sender, body, date)
        ↓
Send to Groq AI (Llama 3.3 70B) in batches of 10
        ↓
AI returns: priority + category + 1-line summary
        ↓
Save to SQLite database
        ↓
Display on beautiful dashboard
```

---

## 🔒 Privacy

- Emails are stored **locally** on your machine (SQLite file)
- Gmail access is **read-only** — the app cannot send, delete, or modify emails
- No data is sent to any external server except the AI API (Groq) for analysis
- Each user can only see their own emails

---

## 📸 Screenshots

> Dashboard with AI-classified emails, priority badges, and category filters

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

MIT License — free to use for personal and commercial projects.

---

**Built with ❤️ using FastAPI + Claude AI**