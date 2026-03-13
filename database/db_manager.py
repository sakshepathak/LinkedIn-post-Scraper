import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'linkedin_data.db')


def get_db_connection():
    """Connects to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the posts table if it does not exist, and migrates if needed."""
    conn = get_db_connection()

    # Create the table with the full schema
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_name TEXT,
            post_text TEXT,
            post_url TEXT UNIQUE,
            timestamp TEXT,
            search_query TEXT DEFAULT '',
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Migration: add search_query column if it doesn't exist yet (for older DBs)
    try:
        conn.execute("SELECT search_query FROM posts LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE posts ADD COLUMN search_query TEXT DEFAULT ''")
        print("ℹ️  Migrated database: added 'search_query' column.")

    conn.commit()
    conn.close()


def save_posts(posts):
    """Saves a list of post dictionaries to the database. Skips duplicates by post_url."""
    conn = get_db_connection()
    added_count = 0
    for post in posts:
        try:
            conn.execute('''
                INSERT INTO posts (author_name, post_text, post_url, timestamp, search_query)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                post.get('author_name', ''),
                post.get('post_text', ''),
                post.get('post_url', ''),
                post.get('timestamp', ''),
                post.get('search_query', ''),
            ))
            added_count += 1
        except sqlite3.IntegrityError:
            # Skip if the post_url already exists (MUST be unique)
            continue
    conn.commit()
    conn.close()
    return added_count


def get_all_queries():
    """Returns a list of distinct search queries stored in the database."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT DISTINCT search_query FROM posts WHERE search_query != '' ORDER BY search_query"
    ).fetchall()
    conn.close()
    return [row["search_query"] for row in rows]


def clear_posts():
    """Deletes all posts from the database. Returns the number of rows deleted."""
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    conn.execute("DELETE FROM posts")
    conn.commit()
    conn.close()
    return count
