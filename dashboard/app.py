"""
LinkedIn Post Scout — Streamlit Dashboard
==========================================
Main entry point. Layout and flow only; styling, API helpers,
and dialog content live in sibling modules.
"""

import streamlit as st
import pandas as pd
import time

from styles import inject_css
from api_client import (
    fetch_posts,
    fetch_queries,
    trigger_scrape,
    get_scrape_status,
    clear_all_data,
)
from how_it_works import show_how_it_works


# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LinkedIn Post Scout",
    page_icon="L",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject all custom CSS (pink theme, hidden deploy bar, polished inputs, etc.)
inject_css()


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## LinkedIn Post Scout")
    st.markdown("---")

    # --- Scrape new posts ---
    st.markdown("### Scrape New Posts")
    scrape_query = st.text_input(
        "Keyword / Company / Author",
        placeholder='e.g. "remote work", Tesla, software engineering',
        help="Enter a keyword, company name, or person's name to search for LinkedIn posts.",
    )
    max_pages = st.slider(
        "Max pages to fetch",
        min_value=1,
        max_value=3,
        value=1,
        help="Each page ~ 10 results. Each page = 1 SerpApi credit.",
    )
    st.caption(
        f"Up to **{max_pages * 10}** posts  |  "
        f"**{max_pages}** API credit{'s' if max_pages > 1 else ''}"
    )

    if st.button("Start Scraping", use_container_width=True, type="primary"):
        if scrape_query.strip():
            code, resp = trigger_scrape(scrape_query.strip(), max_pages)
            if code == 200:
                st.success(f"Scrape started for **{scrape_query}**!")
                with st.spinner("Scraping in progress... this may take a minute."):
                    while True:
                        time.sleep(3)
                        status = get_scrape_status()
                        if not status.get("running", False):
                            break
                if status.get("error"):
                    st.error(f"Scrape error: {status['error']}")
                else:
                    st.success(f"Done. Added **{status.get('last_count', 0)}** new posts.")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
            elif code == 409:
                st.warning("A scrape is already in progress. Please wait.")
            else:
                st.error(f"Error: {resp.get('detail', 'Unknown error')}")
        else:
            st.warning("Please enter a search keyword.")

    st.markdown("---")

    # --- Filter existing posts ---
    st.markdown("### Filter Posts")
    search_text = st.text_input(
        "Search by author or content",
        placeholder="Type to filter...",
    )

    available_queries = fetch_queries()
    query_filter = ""
    if available_queries:
        selected = st.selectbox(
            "Filter by scrape keyword",
            options=["All"] + available_queries,
        )
        if selected != "All":
            query_filter = selected

    result_limit = st.slider("Max results to display", 10, 500, 100, step=10)

    st.markdown("---")

    # --- Clear data ---
    st.markdown("### Clear Data")
    st.caption("Remove all previously scraped posts to start fresh.")
    if st.button("Clear All Data", use_container_width=True):
        result = clear_all_data()
        if "error" in result:
            st.error(f"Failed to clear data: {result['error']}")
        else:
            st.success(f"Cleared {result.get('deleted', 0)} posts.")
            st.cache_data.clear()
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    st.markdown(
        "<div class='sidebar-footer'>"
        "Powered by SerpApi + FastAPI + Streamlit"
        "</div>",
        unsafe_allow_html=True,
    )


# ── Main Content ─────────────────────────────────────────────────────────────

# Header row
header_col, btn_col = st.columns([3, 1])

with header_col:
    st.markdown(
        "<h1 style='background: linear-gradient(135deg, #ff3c78, #ff7eb3); "
        "-webkit-background-clip: text; -webkit-text-fill-color: transparent; "
        "font-size: 2.5rem; margin-bottom: 0;'>LinkedIn Post Scout</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color: #94a3b8; font-size: 1.05rem; margin-top: 0;'>"
        "Search, scrape &amp; explore LinkedIn posts — powered by SerpApi.</p>",
        unsafe_allow_html=True,
    )

with btn_col:
    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    if st.button("How Does This App Work?", use_container_width=True, type="secondary"):
        show_how_it_works()


# Fetch data
posts, total_count = fetch_posts(
    search=search_text, query_filter=query_filter, limit=result_limit
)


# ── Metrics Row ──────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{total_count}</div>'
        f'<div class="metric-label">Posts Found</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    unique_authors = len(
        set(
            p.get("author_name", "")
            for p in posts
            if p.get("author_name") and p["author_name"] != "Unknown Author"
        )
    )
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{unique_authors}</div>'
        f'<div class="metric-label">Unique Authors</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    unique_keywords = len(
        set(p.get("search_query", "") for p in posts if p.get("search_query"))
    )
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{unique_keywords}</div>'
        f'<div class="metric-label">Keywords Tracked</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{len(available_queries)}</div>'
        f'<div class="metric-label">Total Scrapes</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ── Data Table (Expandable) ─────────────────────────────────────────────────
if posts:
    with st.expander("Data Table View", expanded=False):
        df = pd.DataFrame(posts)
        display_cols = [
            c
            for c in [
                "author_name", "post_text", "timestamp",
                "search_query", "post_url", "extracted_at",
            ]
            if c in df.columns
        ]
        df_display = df[display_cols] if display_cols else df

        col_config = {
            "author_name": "Author",
            "post_text": "Post Content",
            "timestamp": "Date",
            "search_query": "Keyword",
            "post_url": st.column_config.LinkColumn("Post URL"),
            "extracted_at": "Scraped At",
        }

        st.dataframe(
            df_display,
            column_config=col_config,
            hide_index=True,
            use_container_width=True,
            height=350,
        )

    # ── Card View ────────────────────────────────────────────────────────────
    st.markdown("### Posts")

    for post in posts:
        author = post.get("author_name", "Unknown Author")
        timestamp = post.get("timestamp", "Date not available")
        text = post.get("post_text", "")
        url = post.get("post_url", "#")
        keyword = post.get("search_query", "")

        author_html = (
            f'<span class="author-badge">{author}</span>'
            if author and author != "Unknown Author"
            else '<span class="author-badge">Unknown</span>'
        )
        date_html = (
            f'<span class="date-badge">{timestamp}</span>'
            if timestamp and timestamp != "Date not available"
            else ""
        )
        keyword_html = (
            f'<span class="search-keyword">{keyword}</span>' if keyword else ""
        )

        card_html = f"""
        <div class="post-card">
            <div style="margin-bottom: 0.6rem;">
                {author_html}{date_html}{keyword_html}
            </div>
            <p style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.6; margin: 0.5rem 0;">
                {text}
            </p>
            <a href="{url}" target="_blank"
               style="color: #ff7eb3; text-decoration: none; font-size: 0.85rem;">
                View on LinkedIn &rarr;
            </a>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

else:
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem; color: #94a3b8;">
            <h3>No posts found</h3>
            <p>Use the sidebar to <strong>scrape new posts</strong> by entering
            a keyword, company, or author name.<br>
            Or adjust your filters to see existing data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
