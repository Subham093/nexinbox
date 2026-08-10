#  test_basic.py — A few real, automated tests

# These test the "pure functions" in gmail.py — functions that
# take an input and always return the same output, with no
# network calls or database involved. That makes them easy and
# fast to test automatically.
#
# Run locally with:   pytest -v
# Runs automatically in CI on every push (see .github/workflows/ci.yml)



from gmail import (
    extract_sender_name,
    extract_email_address,
    clean_snippet,
    parse_email_date,
)

#  Tests for extract_sender_name()

def test_extract_sender_name_with_quotes():
    """A normal 'Name <email>' sender should return just the name."""
    result = extract_sender_name('"John Doe" <john@example.com>')
    assert result == "John Doe"


def test_extract_sender_name_without_quotes():
    """Works even if the name isn't wrapped in quotes."""
    result = extract_sender_name("Jane Smith <jane@example.com>")
    assert result == "Jane Smith"


def test_extract_sender_name_only_email():
    """If there's no name at all, just an email, it should still work."""
    result = extract_sender_name("noreply@company.com")
    assert result == "noreply@company.com"


#  Tests for extract_email_address()

def test_extract_email_address_normal():
    """Should correctly pull the email out of 'Name <email>' format."""
    result = extract_email_address("John Doe <john@example.com>")
    assert result == "john@example.com"


def test_extract_email_address_plain():
    """If it's already just a plain email, return it as-is."""
    result = extract_email_address("plain@example.com")
    assert result == "plain@example.com"


#  Tests for clean_snippet()

def test_clean_snippet_unescapes_html_entities():
    """Gmail sometimes sends snippets with HTML-escaped characters like &amp;"""
    result = clean_snippet("Terms &amp; Conditions apply")
    assert result == "Terms & Conditions apply"


def test_clean_snippet_handles_empty_string():
    """Should not crash on an empty snippet."""
    result = clean_snippet("")
    assert result == ""


#  Tests for parse_email_date()

def test_parse_email_date_standard_format():
    """A UTC email date should now be converted to IST (UTC+5:30) to match Gmail's own display."""
    result = parse_email_date("Mon, 15 Jan 2024 10:30:00 +0000")
    assert result == "2024-01-15 16:00:00"

def test_parse_email_date_handles_empty_string():
    """If no date is provided, it should fall back gracefully instead of crashing."""
    result = parse_email_date("")
    # We just check it returns SOME valid-looking timestamp string,
    # since it falls back to "now" when no date is given.
    assert len(result) == 19  # "YYYY-MM-DD HH:MM:SS" is always 19 characters