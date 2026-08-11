#  test_basic.py — A few real, automated tests
# These test the "pure functions" in gmail.py — functions that
# take an input and always return the same output, with no
# network calls or database involved. That makes them easy and
# fast to test automatically.
#
# Run locally with:   pytest -v
# Runs automatically in CI on every push (see .github/workflows/ci.yml)
#
# UPDATED: added coverage for strip_html(), clean_text(), and expanded
# clean_snippet() — these were previously untested despite being
# rewritten (strip_html moved from regex-based tag matching to a real
# html.parser.HTMLParser implementation; clean_text/clean_snippet
# gained invisible-Unicode stripping, URL shortening, and comma-spacing
# fixes). Each test below reflects an actual scenario that was manually
# verified during that work — not hypothetical cases.

from gmail import (
    extract_sender_name,
    extract_email_address,
    clean_snippet,
    parse_email_date,
    strip_html,
    clean_text,
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


def test_clean_snippet_strips_invisible_unicode():
    """
    Some marketing platforms (e.g. an Unstop email seen in production)
    pad text with invisible zero-width Unicode characters (U+FEFF,
    U+034F, etc.) to manipulate email-client preview text. Since
    email_detail.html falls back to displaying the snippet directly
    when an email has no parsed body, this junk needs to be stripped
    here too, not just in clean_text().
    """
    junk = "Apply Today!  \ufeff \u034f  \ufeff \u034f  Hi Subham, your profile stood out."
    result = clean_snippet(junk)
    assert "\ufeff" not in result
    assert "\u034f" not in result
    assert result == "Apply Today! Hi Subham, your profile stood out."


#  Tests for strip_html()
#  (rewritten to use html.parser.HTMLParser instead of regex —  these confirm it handles real-world HTML correctly)

def test_strip_html_preserves_paragraph_breaks():
    """<p> tags should become real line breaks, not get flattened away."""
    html = "<p>First paragraph.</p><p>Second paragraph.</p>"
    result = strip_html(html)
    assert "First paragraph." in result
    assert "Second paragraph." in result
    # The two paragraphs must NOT be on the same line.
    lines = [l for l in result.split("\n") if l.strip()]
    assert "First paragraph." in lines
    assert "Second paragraph." in lines


def test_strip_html_converts_br_to_newline():
    """<br> tags should become real line breaks."""
    html = "Line one<br>Line two"
    result = strip_html(html)
    assert "\n" in result


def test_strip_html_list_items_get_bullets():
    """<li> items should be split onto their own lines with a bullet,
    so numbered/bulleted newsletter content doesn't collapse into one
    run-on line."""
    html = "<ul><li>Item one</li><li>Item two</li></ul>"
    result = strip_html(html)
    assert "• Item one" in result
    assert "• Item two" in result


def test_strip_html_excludes_script_and_style_content():
    """Text inside <script> and <style> tags must never leak into the
    visible output."""
    html = "<style>.x{color:red}</style><p>Real content</p><script>alert('bad')</script>"
    result = strip_html(html)
    assert "Real content" in result
    assert "color:red" not in result
    assert "alert" not in result


def test_strip_html_table_cells_stay_separated():
    """
    Table-layout emails (common in older marketing HTML) must not glue
    adjacent cell text together. This was a real bug found while
    testing the HTMLParser rewrite — <td>Row 1</td><td>Row 2</td> was
    rendering as "Row 1Row 2" before td/th were given explicit handling.
    """
    html = "<table><tr><td>Row 1 Col 1</td><td>Row 1 Col 2</td></tr></table>"
    result = strip_html(html)
    assert "Row 1 Col 1 Row 1 Col 2" in result
    assert "Col 1Row" not in result  # the glued-together bug, explicitly


def test_strip_html_handles_malformed_unclosed_tags():
    """
    Real marketing HTML is often malformed (unclosed tags, mismatched
    nesting). HTMLParser should degrade gracefully instead of crashing
    the whole email fetch.
    """
    html = "<p>Unclosed paragraph <b>bold text without closing<p>Next para</p>"
    result = strip_html(html)  # must not raise
    assert "Unclosed paragraph" in result
    assert "Next para" in result


def test_strip_html_decodes_entities():
    """HTML entities (&amp;, &mdash;, numeric character refs) should be
    decoded automatically, not left as literal escape sequences."""
    html = "<p>Terms &amp; Conditions &mdash; apply</p>"
    result = strip_html(html)
    assert "&amp;" not in result
    assert "Terms & Conditions" in result


#  Tests for clean_text()

def test_clean_text_preserves_line_breaks():
    """
    Previously, clean_text() joined every line with a single space,
    destroying paragraph structure even when strip_html() had correctly
    produced real newlines. This should no longer happen — the frontend
    renders with white-space: pre-wrap, so real newlines must survive.
    """
    text = "First paragraph.\nSecond paragraph."
    result = clean_text(text)
    assert "\n" in result
    assert result != "First paragraph. Second paragraph."


def test_clean_text_strips_invisible_unicode():
    """Same invisible-character junk as the clean_snippet test, but for
    the full email body path."""
    junk = "TVS Credit E.P.I.C. 8.0 Apply Today!  \ufeff \u034f  \ufeff \u034f \nHi Subham,"
    result = clean_text(junk)
    assert "\ufeff" not in result
    assert "\u034f" not in result
    assert "TVS Credit E.P.I.C. 8.0 Apply Today!" in result


def test_clean_text_shortens_long_urls():
    """
    Long tracking/redirect URLs (common in newsletter HTML, e.g.
    LinkedIn's tracking links) should be shortened so they don't
    dominate the visible text. Short URLs (<=60 chars) stay untouched.
    """
    long_url = "https://www.linkedin.com/comm/pulse/5-must-reads-weekend?lipi=urn%3Ali%3Apage%3Aemail_email_series_follow_newsletter_O2"
    result = clean_text(f"Check this out: {long_url}")
    assert long_url not in result
    assert "…" in result

    short_url = "https://example.com/a"
    result2 = clean_text(f"Visit {short_url}")
    assert short_url in result2


def test_clean_text_fixes_missing_comma_spacing():
    """
    Some sender HTML (e.g. a real Myntra email) renders comma-separated
    lists with no space after the comma, because the visual gap in the
    original came from CSS rather than an actual space character.
    """
    result = clean_text("clothing,footwear,accessories, jewellery")
    assert result == "clothing, footwear, accessories, jewellery"


def test_clean_text_does_not_add_space_in_numbers():
    """
    The comma-spacing fix must NOT touch thousands separators or order
    numbers — only commas followed by a letter get a space added.
    """
    result = clean_text("Total: ₹10,000 for order #12,345,678")
    assert result == "Total: ₹10,000 for order #12,345,678"


def test_clean_text_collapses_repeated_blank_lines():
    """Multiple consecutive blank lines should collapse to a single
    paragraph break, not a wall of empty space."""
    text = "Paragraph one.\n\n\n\n\nParagraph two."
    result = clean_text(text)
    assert "\n\n\n" not in result


def test_clean_text_handles_empty_string():
    """Should not crash on empty input."""
    result = clean_text("")
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