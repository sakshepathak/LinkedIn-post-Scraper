import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database.db_manager import get_db_connection, init_db, save_posts, get_all_queries, clear_posts

app = FastAPI(title="LinkedIn Scraper API", version="2.0.0")

# Allow requests from the Streamlit dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize DB on startup
@app.on_event("startup")
def startup_event():
    init_db()


# --- Request / Response Models ---
class ScrapeRequest(BaseModel):
    query: str = '"Adya AI"'
    max_pages: int = 1


# --- In-memory scrape status tracker ---
_scrape_status = {"running": False, "last_query": "", "last_count": 0, "error": ""}


def _run_scrape(query: str, max_pages: int):
    """Background task that runs the scraper and saves results."""
    global _scrape_status
    _scrape_status["running"] = True
    _scrape_status["last_query"] = query
    _scrape_status["error"] = ""
    try:
        from scraper.linkedin_scraper import scrape_linkedin_posts
        posts = scrape_linkedin_posts(query=query, max_pages=max_pages)
        if posts:
            added = save_posts(posts)
            _scrape_status["last_count"] = added
        else:
            _scrape_status["last_count"] = 0
    except Exception as e:
        _scrape_status["error"] = str(e)
    finally:
        _scrape_status["running"] = False


# --- Endpoints ---

@app.get("/")
def read_root():
    """Welcome endpoint for the API"""
    return {"message": "Welcome to the LinkedIn Scraper API v2. Endpoints: /posts, /scrape, /scrape-status, /queries"}


@app.get("/posts")
def get_posts(limit: int = 100, search: str = None, query_filter: str = None):
    """
    Returns the scraped posts from the SQLite database.
    - search:       filter by author name or post content
    - query_filter: filter by the original search query keyword
    """
    conn = get_db_connection()

    conditions = []
    params = []

    if search:
        conditions.append("(post_text LIKE ? OR author_name LIKE ?)")
        pattern = f"%{search}%"
        params.extend([pattern, pattern])

    if query_filter:
        conditions.append("search_query LIKE ?")
        params.append(f"%{query_filter}%")

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    sql = f"SELECT * FROM posts {where_clause} ORDER BY extracted_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    posts = [dict(row) for row in rows]
    return {"count": len(posts), "posts": posts}


@app.post("/scrape")
def start_scrape(req: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Triggers a background scrape. Returns immediately while the scrape runs.
    Check /scrape-status for progress.
    """
    if _scrape_status["running"]:
        raise HTTPException(status_code=409, detail="A scrape is already in progress. Please wait.")

    background_tasks.add_task(_run_scrape, req.query, req.max_pages)
    return {"message": f"Scrape started for '{req.query}' (max {req.max_pages} pages). Check /scrape-status."}


@app.get("/scrape-status")
def scrape_status():
    """Returns the current status of the background scraper."""
    return _scrape_status


@app.get("/queries")
def list_queries():
    """Returns all distinct search queries stored in the database."""
    return {"queries": get_all_queries()}


@app.delete("/clear")
def clear_all_posts():
    """Deletes all scraped posts from the database."""
    deleted = clear_posts()
    return {"message": f"Cleared {deleted} posts from the database.", "deleted": deleted}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
