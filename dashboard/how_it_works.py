"""
"How LinkedIn Post Scout Works" dialog content.
Separated from app.py to keep the main file focused on layout.
"""

import streamlit as st


# ── FAQ data ─────────────────────────────────────────────────────────────────
FAQ_ITEMS = [
    (
        "Does this app require a LinkedIn account?",
        "No. The app never logs in to LinkedIn. It finds public posts through "
        "Google search results, so no LinkedIn credentials are needed at all.",
    ),
    (
        "What is SerpApi and do I need to pay for it?",
        "SerpApi is a service that returns Google search results as structured "
        'data. They offer a free plan with 100 searches per month, which is more '
        'than enough for casual use. Each "page" of scraping uses one search credit.',
    ),
    (
        "Can it scrape posts from private or connections-only LinkedIn profiles?",
        "No. It can only find posts that are publicly visible and have been indexed "
        "by Google. Private posts, posts limited to connections, and posts from "
        "private profiles will not appear in the results.",
    ),
    (
        "Why do some posts show Unknown Author or Date not available?",
        "The author name and date are extracted from Google's search result "
        "snippets, not from LinkedIn directly. Sometimes Google truncates or "
        "reformats titles in a way that makes the author name hard to parse. "
        "The app tries multiple patterns to extract the name, but it does not "
        "always work perfectly. Similarly, timestamps are decoded from the "
        "LinkedIn activity ID in the URL when possible, but this is not "
        "available for every post.",
    ),
    (
        "Is my data sent anywhere?",
        "The only outbound request is the search query sent to SerpApi. "
        "Everything else runs locally. The database, the API server, and the "
        "dashboard all run on your own machine. Nothing is uploaded or shared.",
    ),
    (
        "Can I use this for any keyword, not just Adya AI?",
        'Yes, absolutely. The default query is set to "Adya AI" as a starting '
        "point, but you can type any keyword, company name, person's name, or "
        "phrase into the search box. It works with anything Google can find on "
        "linkedin.com/posts.",
    ),
]


# ── Section helper ───────────────────────────────────────────────────────────
def _section(title: str, *paragraphs: str):
    """Render a styled section block inside the dialog."""
    paras = "".join(f'<p class="section-text">{p}</p>' for p in paragraphs)
    st.markdown(
        f'<div class="section-block">'
        f'<div class="section-title">{title}</div>'
        f"{paras}</div>",
        unsafe_allow_html=True,
    )


# ── Dialog ───────────────────────────────────────────────────────────────────
@st.dialog("How LinkedIn Post Scout Works", width="large")
def show_how_it_works():
    """Renders the explanation dialog using native Streamlit components."""

    # The Big Picture
    _section(
        "The Big Picture",
        "You type a keyword, a company name, or a person's name into the sidebar. "
        "The app then goes out and finds public LinkedIn posts matching that query. "
        "It collects the results, stores them in a lightweight database, and shows "
        "them right here in the dashboard so you can search, filter, and browse "
        "everything in one place.",
        "The whole thing runs locally on your machine. There is no cloud service, "
        "no external server, and no data leaves your computer except the search "
        "request itself.",
    )

    # The Architecture
    _section(
        "The Architecture (Three Simple Pieces)",
        "The project is split into three parts that each handle one job:",
        '<strong style="color:#ff7eb3;">The Scraper</strong> is a Python script '
        "that talks to SerpApi. When you click \"Start Scraping\", it constructs a "
        "Google search query scoped to linkedin.com/posts, sends it off, and parses "
        "the results. It pulls out the author name, post text, timestamp, and the "
        "original LinkedIn URL from each result. Once done, it hands everything "
        "over to the database layer.",
        '<strong style="color:#ff7eb3;">The API</strong> is a small FastAPI server '
        "running on port 8000. It sits between the dashboard and the rest of the "
        "system. It exposes clean endpoints for fetching posts, triggering new "
        "scrapes, checking scrape progress, and clearing data. The scrape itself "
        "runs in the background so the API stays responsive and the dashboard can "
        "poll for updates.",
        '<strong style="color:#ff7eb3;">The Dashboard</strong> is this Streamlit '
        "app you are looking at. It sends requests to the API, gets back JSON "
        "data, and renders everything into the cards and tables you see on screen. "
        "It handles the filtering, search, and display logic.",
    )

    # How the Scraping Works
    _section(
        "How the Scraping Actually Works",
        "LinkedIn does not offer a public API for searching posts by keyword. "
        "If you try to scrape LinkedIn directly, you will run into login walls, "
        "CAPTCHAs, and rate limits very quickly. That is why this project uses a "
        "different approach.",
        "Instead of hitting LinkedIn directly, the scraper searches Google with "
        'the query <strong style="color:#ff7eb3;">site:linkedin.com/posts '
        "[your keyword]</strong>. Google has already indexed millions of public "
        "LinkedIn posts, so this gives us reliable results without ever needing "
        "to log in to LinkedIn or deal with its anti-bot protections.",
        "The actual Google search is handled through SerpApi, which is a third "
        "party service that provides structured, machine-readable Google search "
        "results via a simple REST API. You send it a search query, and it "
        "returns clean JSON with titles, snippets, URLs, and metadata.",
    )

    # Why SerpApi
    _section(
        "Why SerpApi Instead of Something Else",
        "There are several ways you could approach this. Here is why SerpApi "
        "was chosen over the alternatives:",
        '<strong style="color:#ff7eb3;">Direct LinkedIn scraping</strong> '
        "(using Selenium or Playwright to log in and scroll through LinkedIn) "
        "is fragile. LinkedIn actively detects and blocks bots. Your account "
        "can get restricted, the page layout changes often, and you would need "
        "to maintain login sessions and handle two factor authentication. It "
        "works for small experiments but breaks often in practice.",
        '<strong style="color:#ff7eb3;">LinkedIn\'s official API</strong> '
        "requires an approved developer application, and even then, post search "
        "is not available through their API. Their API is designed for things "
        "like managing company pages and posting content, not for discovering "
        "public posts by keyword.",
        '<strong style="color:#ff7eb3;">Raw Google scraping</strong> (sending '
        "HTTP requests to google.com and parsing the HTML) is possible but "
        "unreliable. Google changes its HTML structure, serves CAPTCHAs, and "
        "can block your IP. You would spend more time debugging the scraper "
        "than using it.",
        '<strong style="color:#ff7eb3;">SerpApi</strong> handles all of that '
        "complexity. It manages proxy rotation, CAPTCHA solving, and HTML "
        "parsing on their end. You get clean JSON results, consistent "
        "formatting, and a generous free tier (100 searches per month). It "
        "just works.",
    )

    # The Database
    _section(
        "The Database",
        "Posts are stored in a local SQLite database file called linkedin_data.db. "
        "SQLite was chosen because it requires zero setup. There is no database "
        "server to install or configure. The file sits right in the project folder "
        "and the app reads and writes to it directly.",
        "Each post is stored with the author name, post text, URL, timestamp, the "
        "keyword that was used to find it, and the date it was scraped. The post "
        "URL is used as a unique key, so if you scrape the same keyword twice, "
        "duplicate posts are automatically skipped.",
    )

    # FAQs
    st.markdown(
        '<div class="section-block">'
        '<div class="section-title">Frequently Asked Questions</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    for q, a in FAQ_ITEMS:
        st.markdown(
            f'<div style="color: #ff7eb3; font-weight: 600; '
            f'font-size: 0.95rem; margin-top: 0.8rem;">{q}</div>',
            unsafe_allow_html=True,
        )
        st.caption(a)
