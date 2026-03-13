import os
import re
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Ensure database module can be imported irrespective of where the script runs
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_manager import save_posts, init_db

# Load environment variables (.env file)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def _extract_author(item: dict) -> str:
    """
    Extract the author name from a SerpApi result.
    Checks the 'source' field first (most reliable, e.g. "LinkedIn · Author Name"),
    then falls back to title-based pattern matching.
    """
    # --- Best source: the 'source' field (e.g. "LinkedIn · Andrew Ng") ---
    source = item.get("source", "")
    if source:
        for sep in ["·", "•", "|", "-", "–", "—"]:
            if sep in source:
                for part in source.split(sep):
                    part = part.strip()
                    if part.lower() != "linkedin" and part and len(part) < 80:
                        return part

    # --- Fallback: parse from title ---
    title = item.get("title", "")

    # Pattern 1: "Name on LinkedIn"
    if " on LinkedIn" in title:
        return title.split(" on LinkedIn")[0].strip()

    # Pattern 2: "Name's Post"
    match = re.search(r"^(.+?)['']s\s+Post", title)
    if match:
        return match.group(1).strip()

    # Pattern 3: "Post from Name | LinkedIn" or "Post by Name | LinkedIn"
    match = re.search(r"(?:Post (?:from|by))\s+(.+?)(?:\s*[\|–\-])", title, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Pattern 4: "Title | Author Name" (author after last pipe, skip "LinkedIn")
    if " | " in title:
        candidate = title.rsplit(" | ", 1)[-1].strip()
        if candidate.lower() != "linkedin" and len(candidate) < 60:
            return candidate

    # Pattern 5: "Name - … | LinkedIn"
    if " - " in title:
        candidate = title.split(" - ")[0].strip()
        if len(candidate) < 60:
            return candidate

    return "Unknown Author"


def _extract_timestamp(item: dict) -> str:
    """
    Try to pull a meaningful date/time string from a SerpApi result.
    First tries decoding the LinkedIn activity ID from the URL (most reliable),
    then falls back to other fields.
    """
    # --- Best source: decode the activity ID from the LinkedIn post URL ---
    link = item.get("link", "")
    aid_match = re.search(r"activity[_-](\d{19})", link)
    if aid_match:
        try:
            activity_id = int(aid_match.group(1))
            timestamp_ms = activity_id >> 22  # first 41 bits = ms since epoch
            dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
            return dt.strftime("%b %d, %Y")
        except (ValueError, OSError, OverflowError):
            pass

    # Direct date field
    date = item.get("date")
    if date:
        return date

    # Sometimes the date is in the rich snippet
    rich_snippet = item.get("rich_snippet", {})
    top = rich_snippet.get("top", {})
    detected_exts = top.get("detected_extensions", {})
    if "posted" in detected_exts:
        return detected_exts["posted"]

    # Try to extract a date-like string from the snippet itself
    snippet = item.get("snippet", "")
    date_match = re.search(
        r"(\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b"
        r"|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b"
        r"|\b\d{1,2}/\d{1,2}/\d{2,4}\b"
        r"|\b\d+ (?:hours?|days?|weeks?|months?) ago\b)",
        snippet,
        re.IGNORECASE,
    )
    if date_match:
        return date_match.group(0)

    return "Date not available"


def scrape_linkedin_posts(query='"Adya AI"', max_pages=1):
    """
    Uses SerpApi to search Google for LinkedIn posts.
    Paginates through multiple pages to gather more results.

    Args:
        query:     The search keyword/phrase (e.g., '"Adya AI"', 'Pratyush', 'Microsoft').
        max_pages: Maximum number of Google result pages to fetch (1 page ≈ 10 results).
                   Each page costs 1 SerpApi credit.

    Returns:
        A list of post dicts with keys: author_name, post_text, post_url, timestamp, search_query.
    """
    if not SERPAPI_KEY:
        print("Error: SERPAPI_KEY not found in .env file.")
        print("Please sign up at https://serpapi.com/ and put your key in a .env file.")
        return []

    print(f"🔎 Scraping LinkedIn posts for: {query}")
    print(f"   Max pages to fetch: {max_pages} (≈ {max_pages * 10} results max)")

    # We construct the search query targeting linkedin posts
    search_query = f"site:linkedin.com/posts {query}"

    all_results = []

    for page in range(max_pages):
        start = page * 10  # Google pagination offset

        params = {
            "engine": "google",
            "q": search_query,
            "tbs": "qdr:m6",       # Restrict search to the last 6 months
            "api_key": SERPAPI_KEY,
            "num": 10,              # Results per page (Google max is ~10 for organic)
            "start": start,         # Pagination offset
        }

        print(f"   📄 Fetching page {page + 1}/{max_pages} (offset={start})...")

        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"   ❌ Error on page {page + 1}: {e}")
            break

        organic = data.get("organic_results", [])

        if not organic:
            print(f"   ℹ️  No more results on page {page + 1}. Stopping pagination.")
            break

        for item in organic:
            title = item.get("title", "")
            post_url = item.get("link", "")

            # Only keep actual LinkedIn post URLs
            if "linkedin.com/posts" not in post_url:
                continue

            author_name = _extract_author(item)
            post_text = item.get("snippet", "")
            timestamp = _extract_timestamp(item)

            all_results.append({
                "author_name": author_name,
                "post_text": post_text,
                "post_url": post_url,
                "timestamp": timestamp,
                "search_query": query,  # Track which keyword produced this result
            })

        # Be polite: small delay between pages to avoid rate-limiting
        if page < max_pages - 1:
            time.sleep(1.5)

    print(f"\n✅ Total posts found: {len(all_results)}")
    return all_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape LinkedIn posts via SerpApi")
    parser.add_argument(
        "-q", "--query",
        type=str,
        default='"Adya AI"',
        help='Search query, e.g. \'"Adya AI"\' or \'Microsoft\' or \'Pratyush\' (default: "Adya AI")',
    )
    parser.add_argument(
        "-p", "--pages",
        type=int,
        default=1,
        help="Maximum number of Google result pages to fetch (default: 1, max 3, each page ≈ 10 results)",
    )

    args = parser.parse_args()

    # 1. Initialize the database table
    init_db()

    # 2. Run the scraper logic
    extracted_posts = scrape_linkedin_posts(query=args.query, max_pages=args.pages)

    # 3. Save results to the database safely
    if extracted_posts:
        added = save_posts(extracted_posts)
        print(f"💾 Successfully saved {added} new posts to the database (skipped duplicates).")
    else:
        print("No posts found or saved.")
