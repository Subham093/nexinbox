#  evaluate_ai.py — Measure AI Classification Accuracy
# Run this file AFTER fetching emails to measure how accurate the AI classification is.
# How it works:
#   1. Loads your emails from the database
#   2. You manually label a sample (20-30 emails)
#   3. Compares AI labels vs your manual labels
#   4. Prints accuracy score + confusion matrix

# NOTE: This now reuses database.py's PostgreSQL/Supabase connection —
# it used to connect to a local SQLite file directly, which stopped
# reflecting reality once the app migrated off SQLite. Always evaluate
# against the real, live data.
# Run: python evaluate_ai.py

from collections import defaultdict
from database import get_db


#  STEP 1: Print all emails with AI labels
#  (You will manually decide if they're correct)

def print_emails_for_review(user_email: str, limit: int = 30):
    """Prints emails with their AI classifications for manual review."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT gmail_id, subject, sender, priority, category, ai_summary
            FROM emails WHERE user_email = %s
            ORDER BY date DESC LIMIT %s
        """, (user_email, limit))
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    print(f"\n{'='*80}")
    print(f"📧 EMAILS FOR MANUAL REVIEW ({len(rows)} emails)")
    print(f"{'='*80}\n")

    for i, row in enumerate(rows):
        print(f"[{i+1:2d}] Subject : {row['subject'][:60]}")
        print(f"     Sender  : {row['sender'][:40]}")
        print(f"     AI said : Priority={row['priority'].upper():<8} Category={row['category']}")
        print(f"     Summary : {row['ai_summary'][:80] if row['ai_summary'] else 'N/A'}")
        print()

    return [dict(row) for row in rows]


#  STEP 2: Calculate accuracy

def calculate_accuracy(predictions: list, ground_truth: list, label_type: str):
    if len(predictions) != len(ground_truth):
        print("❌ Length mismatch!")
        return 0

    correct = sum(1 for p, g in zip(predictions, ground_truth) if p.lower() == g.lower())
    accuracy = (correct / len(predictions)) * 100

    print(f"\n{'='*50}")
    print(f"📊 {label_type.upper()} ACCURACY REPORT")
    print(f"{'='*50}")
    print(f"Total emails evaluated : {len(predictions)}")
    print(f"Correctly classified   : {correct}")
    print(f"Incorrectly classified : {len(predictions) - correct}")
    print(f"Accuracy Score         : {accuracy:.1f}%")

    return accuracy


#  STEP 3: Confusion Matrix

def print_confusion_matrix(predictions: list, ground_truth: list, labels: list):
    matrix = defaultdict(lambda: defaultdict(int))
    for pred, actual in zip(predictions, ground_truth):
        matrix[actual.lower()][pred.lower()] += 1

    print(f"\n{'='*60}")
    print(f"📊 CONFUSION MATRIX")
    print(f"Rows = Actual | Columns = AI Predicted")
    print(f"{'='*60}")

    col_w = 12
    print(f"{'Actual':>14}", end="")
    for label in labels:
        print(f"{label[:col_w]:>{col_w}}", end="")
    print()
    print("-" * (14 + col_w * len(labels)))

    for actual in labels:
        print(f"{actual[:14]:>14}", end="")
        for pred in labels:
            val = matrix[actual.lower()][pred.lower()]
            print(f"{val:>{col_w}}", end="")
        print()

    print(f"\n✅ Diagonal = correct classifications")
    print(f"❌ Off-diagonal = misclassifications")


#  STEP 4: Per-category breakdown

def per_category_accuracy(predictions: list, ground_truth: list, labels: list):
    print(f"\n{'='*50}")
    print(f"📊 PER-CATEGORY BREAKDOWN")
    print(f"{'='*50}")

    for label in labels:
        actual_indices = [i for i, g in enumerate(ground_truth) if g.lower() == label.lower()]
        if not actual_indices:
            continue

        correct = sum(1 for i in actual_indices if predictions[i].lower() == label.lower())
        total   = len(actual_indices)
        pct     = (correct / total * 100) if total > 0 else 0

        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"{label:<12} [{bar}] {pct:5.1f}%  ({correct}/{total})")


#  MAIN: Run full evaluation

if __name__ == "__main__":
    print("\n🔍 NexInbox AI Accuracy Evaluator")
    print("="*50)

    # ── Get user email ────────────────────────────
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT user_email FROM emails")
        users = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not users:
        print("❌ No emails in database! Fetch emails first.")
        exit()

    user_email = users[0]["user_email"]
    print(f"👤 Evaluating for: {user_email}")

    # ── Print emails for review ───────────────────
    emails = print_emails_for_review(user_email, limit=30)

    if not emails:
        print("❌ No emails found!")
        exit()

    ai_priorities  = [e["priority"] for e in emails]
    ai_categories  = [e["category"] for e in emails]

    print("\n" + "="*80)
    print("📝 MANUAL LABELLING REQUIRED")
    print("="*80)
    print("Look at the emails above and enter correct labels below.")
    print("Press ENTER to accept AI label, or type correct label.\n")

    priority_labels  = ["high", "medium", "low"]
    category_labels  = ["Work", "Finance", "Promotions", "Social", "Newsletters", "Other"]

    manual_priorities  = []
    manual_categories  = []

    print("── PRIORITY LABELS ──")
    print("Options: high / medium / low")
    print("(Press Enter to agree with AI, or type correct answer)\n")

    for i, email in enumerate(emails):
        ai_p = email["priority"]
        print(f"[{i+1:2d}] {email['subject'][:55]}")
        print(f"     AI says: {ai_p.upper()}")
        user_input = input(f"     Your label (Enter={ai_p}): ").strip().lower()
        manual_priorities.append(user_input if user_input in priority_labels else ai_p)
        print()

    print("\n── CATEGORY LABELS ──")
    print("Options: Work / Finance / Promotions / Social / Newsletters / Other")
    print("(Press Enter to agree with AI, or type correct answer)\n")

    for i, email in enumerate(emails):
        ai_c = email["category"]
        print(f"[{i+1:2d}] {email['subject'][:55]}")
        print(f"     AI says: {ai_c}")
        user_input = input(f"     Your label (Enter={ai_c}): ").strip()
        if user_input:
            user_input = user_input.capitalize()
        manual_categories.append(user_input if user_input in category_labels else ai_c)
        print()

    p_accuracy = calculate_accuracy(ai_priorities, manual_priorities, "Priority")
    c_accuracy = calculate_accuracy(ai_categories, manual_categories, "Category")

    print_confusion_matrix(ai_priorities, manual_priorities, priority_labels)
    print_confusion_matrix(ai_categories, manual_categories, category_labels)

    per_category_accuracy(ai_categories, manual_categories, category_labels)

    overall = (p_accuracy + c_accuracy) / 2
    print(f"\n{'='*50}")
    print(f"🎯 OVERALL AI ACCURACY: {overall:.1f}%")
    print(f"   Priority Accuracy : {p_accuracy:.1f}%")
    print(f"   Category Accuracy : {c_accuracy:.1f}%")

    if overall >= 85:
        print(f"\n✅ Excellent! AI is performing very well.")
    elif overall >= 70:
        print(f"\n⚠️  Good. Some improvements possible via prompt tuning.")
    else:
        print(f"\n❌ Needs improvement. Consider refining AI prompt.")

    print(f"\n📋 Evaluated {len(emails)} emails")
    print(f"{'='*50}\n")