"""
fetch_posters.py

One-time enrichment script: looks up each title in media.json against
the TMDb API and adds a "poster" field (a full image URL) to every entry.
Run this locally whenever you want to refresh/add poster art -- the
live webpage never calls the API directly, it just reads the URLs
this script bakes into media.json.

Setup:
    pip install requests

    Create a file called tmdb_key.txt in this same folder containing
    ONLY your TMDb API Key (the short one, not the long Read Access
    Token) -- nothing else, no quotes, no newlines beyond the key itself.

    IMPORTANT: add tmdb_key.txt to your .gitignore so your key never
    gets pushed to GitHub.

Usage:
    python fetch_posters.py
"""

import json
import time
from pathlib import Path

import requests

DATA_FILE = Path(__file__).parent / "media.json"
KEY_FILE = Path(__file__).parent / "tmdb_key.txt"

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w342"


def load_key():
    if not KEY_FILE.exists():
        print(f"Create {KEY_FILE.name} in this folder with your TMDb API key inside, then rerun.")
        raise SystemExit(1)
    return KEY_FILE.read_text().strip()


def search_poster(title, category, api_key):
    endpoint = "movie" if category == "movie" else "tv"
    resp = requests.get(
        f"{BASE_URL}/search/{endpoint}",
        params={"api_key": api_key, "query": title},
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None
    poster_path = results[0].get("poster_path")
    return f"{IMAGE_BASE}{poster_path}" if poster_path else None


def main():
    api_key = load_key()
    items = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    for item in items:
        title = item["title"]
        category = item.get("category", "movie")
        try:
            poster = search_poster(title, category, api_key)
        except requests.RequestException as e:
            print(f"  Error looking up {title}: {e}")
            poster = None

        item["poster"] = poster
        print(f"{title}: {'found' if poster else 'no match'}")

        time.sleep(0.25)  # be polite to the API

    DATA_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nDone. media.json updated with poster URLs.")


if __name__ == "__main__":
    main()
