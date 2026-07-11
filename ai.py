# ============================================================
#  ai.py — The AI Brain (using Groq + Llama 3)
# ============================================================

import os
import json
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "openai/gpt-oss-120b"   # Updated model (llama-3.3 deprecated Aug 16, 2026)   # Updated model


# ══════════════════════════════════════════════════
#  MAIN FUNCTION: Analyze a batch of emails
# ══════════════════════════════════════════════════
async def analyze_emails_batch(emails: list) -> list:
    """
    Takes a list of email dicts, sends them to AI in batches of 10,
    gets back priority + category + summary for each one.
    """
    if not emails:
        return emails

    if not GROQ_API_KEY:
        print("⚠️  No GROQ_API_KEY found — using default values")
        return assign_defaults(emails)

    print(f"🤖 Sending {len(emails)} emails to Groq AI for analysis...")

    batch_size = 10
    results    = []

    for i in range(0, len(emails), batch_size):
        batch = emails[i:i + batch_size]
        print(f"  📦 Processing batch {i//batch_size + 1} ({len(batch)} emails)...")

        try:
            analyzed_batch = await analyze_batch(batch)
            results.extend(analyzed_batch)
        except Exception as e:
            print(f"  ⚠️  Batch {i//batch_size + 1} failed: {e} — using defaults")
            results.extend(assign_defaults(batch))

        # Wait 6 seconds between batches to respect Groq rate limit
        if i + batch_size < len(emails):
            print(f"  ⏳ Waiting 6 seconds before next batch...")
            await asyncio.sleep(6)

    print(f"✅ AI analysis complete for {len(results)} emails!")
    return results


# ══════════════════════════════════════════════════
#  CORE: Send one batch of emails to Groq
# ══════════════════════════════════════════════════
async def analyze_batch(emails: list) -> list:
    """
    Sends a batch of emails to Groq and parses the JSON response.
    """
    email_list = []
    for idx, email in enumerate(emails):
        email_list.append({
            "index": idx,
            "subject": email.get("subject", "")[:200],
            "sender":  email.get("sender_email", email.get("sender", ""))[:100],
            "preview": email.get("snippet", email.get("body", ""))[:300],
        })

    prompt = f"""You are an expert email classifier. Analyze these emails and return ONLY a JSON array.

For each email, determine:
1. priority: "high", "medium", or "low"
2. category: exactly one of: "Work", "Finance", "Promotions", "Social", "Newsletters", "Other"
3. summary: 1 sentence summary of what the email is about

PRIORITY RULES (be strict):
- high: interview calls, job offers, urgent deadlines, payment overdue, account security alerts,
        OTP/verification codes, urgent requests from real humans, legal notices, offer letters
- medium: hiring alerts, internship openings, LinkedIn notifications,
          course reminders, welcome emails → these are MEDIUM not low
- low: ONLY newsletters, pure promotional discount emails, 
       weekly digest emails with no action needed

CATEGORY RULES (read carefully):
- Work: job interviews, offer letters, colleagues, GitHub, project updates, office emails,
        hiring alerts (Google hiring, EY hiring, Genpact hiring, internship openings),
        professional certifications, coding platforms (HackerRank, LeetCode, Kaggle)
- Finance: payments, invoices, bank statements, UPI transactions, order receipts,
           subscription billing, wallet balance, tax, credit card statements
- Promotions: discount offers, sale announcements, coupon codes, free rewards,
              marketing emails from brands (Swiggy, Zomato, Amazon, Flipkart, Myntra),
              "X% off", "limited time offer", referral programs
- Social: LinkedIn connection requests/acceptances, Facebook/Instagram notifications,
          WhatsApp, Twitter/X, friend requests, "I want to connect", profile views
- Newsletters: weekly digests, "5 must reads", blog updates, learning resources,
               Stanford/Coursera/edX content emails, EY via LinkedIn newsletters,
               "top stories", industry news roundups
- Other: ONLY use for OTP codes, account verifications, 
         security alerts from Google/Microsoft/banks.
         When in doubt between Work and Other → choose Work.
         When in doubt between Promotions and Other → choose Promotions.
         When in doubt between Social and Other → choose Social.
         NEVER use Other for hiring emails, job alerts, or LinkedIn emails.

IMPORTANT EXAMPLES:
- "Google Hiring Alert" / "EY is hiring interns" / "Genpact is hiring" → Work, medium
- "Intern with Google, Airbus, HP" from Unstop/LinkedIn → Promotions, low  
- "Security alert" from Google → Other, high
- "MongoDB verification code" / "Your OTP" → Other, high
- "14 profile views" from LinkedIn → Social, low
- "5 must reads" newsletter → Newsletters, low
- "Successful sign-in from new device" → Other, high

Emails to analyze:
{json.dumps(email_list, indent=2)}

Respond with ONLY this JSON format, no other text:
[
  {{"index": 0, "priority": "high", "category": "Work", "summary": "One sentence summary here."}},
  {{"index": 1, "priority": "low", "category": "Promotions", "summary": "One sentence summary here."}}
]"""

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "model":       GROQ_MODEL,
                "messages":    [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens":  2000,
            }
        )

    if response.status_code != 200:
        print(f"  ❌ Groq API error: {response.status_code} — {response.text[:200]}")
        return assign_defaults(emails)

    response_data = response.json()
    ai_text = response_data["choices"][0]["message"]["content"].strip()
    ai_text = ai_text.replace("```json", "").replace("```", "").strip()

    try:
        ai_results = json.loads(ai_text)
    except json.JSONDecodeError as e:
        print(f"  ⚠️  JSON parse error: {e}")
        print(f"  Raw AI response: {ai_text[:300]}")
        return assign_defaults(emails)

    result_map = {item["index"]: item for item in ai_results}

    for idx, email in enumerate(emails):
        ai_data = result_map.get(idx, {})

        priority = ai_data.get("priority", "medium").lower()
        if priority not in ("high", "medium", "low"):
            priority = "medium"

        valid_categories = {"Work", "Finance", "Promotions", "Social", "Newsletters", "Other"}
        category = ai_data.get("category", "Other")
        if category not in valid_categories:
            category = "Other"

        summary = ai_data.get("summary", email.get("snippet", "No summary available."))

        email["priority"]   = priority
        email["category"]   = category
        email["ai_summary"] = summary

    return emails


# ══════════════════════════════════════════════════
#  SINGLE EMAIL: Analyze just one email (for detail page)
# ══════════════════════════════════════════════════
async def analyze_single_email(subject: str, sender: str, body: str) -> dict:
    """Analyzes a single email in detail. Returns {priority, category, summary}"""
    if not GROQ_API_KEY:
        return {"priority": "medium", "category": "Other",
                "summary": "AI analysis unavailable."}

    prompt = f"""Analyze this email and return ONLY JSON.

Subject: {subject[:200]}
From: {sender[:100]}
Body: {body[:1000]}

Return ONLY this JSON:
{{"priority": "high/medium/low", "category": "Work/Finance/Promotions/Social/Newsletters/Other", "summary": "2-3 sentence summary of the email content and any action needed."}}"""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":       GROQ_MODEL,
                    "messages":    [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens":  200,
                }
            )

        ai_text = response.json()["choices"][0]["message"]["content"].strip()
        ai_text = ai_text.replace("```json", "").replace("```", "").strip()
        return json.loads(ai_text)

    except Exception as e:
        print(f"⚠️  Single email analysis failed: {e}")
        return {"priority": "medium", "category": "Other",
                "summary": "Could not generate summary."}


# ══════════════════════════════════════════════════
#  FALLBACK: Assign default values without AI
# ══════════════════════════════════════════════════
def assign_defaults(emails: list) -> list:
    """Used when AI is unavailable. Uses keyword matching."""
    for email in emails:
        subject  = (email.get("subject", "") or "").lower()
        sender   = (email.get("sender",  "") or "").lower()
        snippet  = (email.get("snippet", "") or "").lower()
        combined = f"{subject} {sender} {snippet}"

        high_keywords = ["urgent", "invoice", "payment due", "interview",
                         "offer letter", "deadline", "action required",
                         "verify", "security", "alert", "immediately"]
        low_keywords  = ["unsubscribe", "newsletter", "promotion", "offer",
                         "discount", "sale", "% off", "deal", "marketing",
                         "noreply", "no-reply", "notifications@"]

        if any(kw in combined for kw in high_keywords):
            email["priority"] = "high"
        elif any(kw in combined for kw in low_keywords):
            email["priority"] = "low"
        else:
            email["priority"] = "medium"

        if any(kw in combined for kw in ["github", "jira", "meeting", "project",
                                          "team", "office", "work", "job", "interview",
                                          "colleague", "manager"]):
            email["category"] = "Work"
        elif any(kw in combined for kw in ["invoice", "payment", "bank", "transaction",
                                            "order", "receipt", "bill", "amount due",
                                            "credit", "debit", "wallet"]):
            email["category"] = "Finance"
        elif any(kw in combined for kw in ["linkedin", "facebook", "instagram",
                                            "twitter", "whatsapp", "friend request",
                                            "connection", "follow"]):
            email["category"] = "Social"
        elif any(kw in combined for kw in ["newsletter", "digest", "weekly",
                                            "monthly", "subscribe", "blog"]):
            email["category"] = "Newsletters"
        elif any(kw in combined for kw in ["offer", "discount", "sale", "deal",
                                            "% off", "coupon", "promo", "shop",
                                            "swiggy", "zomato", "amazon", "flipkart"]):
            email["category"] = "Promotions"
        else:
            email["category"] = "Other"

        if not email.get("ai_summary"):
            email["ai_summary"] = email.get("snippet", "No preview available.")

    return emails


# ══════════════════════════════════════════════════
#  TEST
# ══════════════════════════════════════════════════
if __name__ == "__main__":
    test_emails = [
        {
            "gmail_id": "test1", "user_email": "test@gmail.com",
            "subject": "Your interview is scheduled for Monday",
            "sender": "HR Team <hr@company.com>", "sender_email": "hr@company.com",
            "snippet": "Dear candidate, your technical interview is scheduled for Monday 10am.",
            "body": "Dear candidate, your technical interview is scheduled for Monday 10am.",
            "date": "2024-01-15", "priority": "", "category": "", "ai_summary": ""
        },
        {
            "gmail_id": "test2", "user_email": "test@gmail.com",
            "subject": "50% off sale this weekend only!",
            "sender": "Myntra <noreply@myntra.com>", "sender_email": "noreply@myntra.com",
            "snippet": "Huge sale this weekend. Up to 50% off on all brands.",
            "body": "Huge sale this weekend. Up to 50% off on all brands. Shop now!",
            "date": "2024-01-15", "priority": "", "category": "", "ai_summary": ""
        },
    ]

    async def test():
        print("🧪 Testing AI analysis...")
        results = await analyze_emails_batch(test_emails)
        for r in results:
            print(f"\n📧 {r['subject']}")
            print(f"   Priority : {r['priority']}")
            print(f"   Category : {r['category']}")
            print(f"   Summary  : {r['ai_summary']}")
        print("\n✅ ai.py is working!")

    asyncio.run(test())