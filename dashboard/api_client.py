"""
API client helpers for the LinkedIn Post Scout dashboard.
Wraps all HTTP calls to the FastAPI backend.
"""

import streamlit as st
import requests

API_URL = "http://localhost:8000"


def fetch_posts(search="", query_filter="", limit=100):
    """Fetch posts from the FastAPI backend."""
    try:
        params = {"limit": limit}
        if search:
            params["search"] = search
        if query_filter:
            params["query_filter"] = query_filter
        response = requests.get(f"{API_URL}/posts", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("posts", []), data.get("count", 0)
    except requests.exceptions.RequestException as e:
        st.error(
            f"Could not connect to the API at `{API_URL}`. "
            f"Make sure the FastAPI server is running.\n\nError: `{e}`"
        )
        return [], 0


def fetch_queries():
    """Get the list of distinct search queries from the database."""
    try:
        response = requests.get(f"{API_URL}/queries", timeout=5)
        response.raise_for_status()
        return response.json().get("queries", [])
    except Exception:
        return []


def trigger_scrape(query, max_pages):
    """Trigger a background scrape via the API."""
    try:
        response = requests.post(
            f"{API_URL}/scrape",
            json={"query": query, "max_pages": max_pages},
            timeout=10,
        )
        return response.status_code, response.json()
    except requests.exceptions.RequestException as e:
        return 500, {"detail": str(e)}


def get_scrape_status():
    """Check the background scraper status."""
    try:
        response = requests.get(f"{API_URL}/scrape-status", timeout=5)
        return response.json()
    except Exception:
        return {"running": False}


def clear_all_data():
    """Clear all scraped posts via the API."""
    try:
        response = requests.delete(f"{API_URL}/clear", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
