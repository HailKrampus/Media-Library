"""
fetch_posters.py

One-time enrichment script: looks up each title in media.json against
the TMDb API and adds a "poster" field (a full image URL) to every entry.
Run this locally whenever you want to refresh/add poster art -- the
live webpage never calls the API directly, it just reads the URLs
this script bakes into media.json.

- TV titles get "Season X" / "Volume X" / disc-count suffixes stripped
  before searching (TMDb indexes shows by name only).
- All titles get trailing parentheticals stripped too, e.g. "(Unrated)",
  "(Director's Cut)", "(Extended Edition)" -- these almost never appear
  in TMDb's actual title.
- If a search comes up empty, it automatically retries against the
  other content type (movie vs. TV), since a few titles (miniseries,
  web series) are filed differently than you'd expect.
- A few titles are box sets/trilogies/compilations with no single
  real release title -- those use a manual override pointing at a
  representative film, or are left without art if there's no
  sensible single match (see MANUAL_OVERRIDES and the SKIP note below).

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
import re
import time
from pathlib import Path

import requests

DATA_FILE = Path(__file__).parent / "media.json"
KEY_FILE = Path(__file__).parent / "tmdb_key.txt"

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w342"

# title -> (search query, forced endpoint or None to use the item's own category)
MANUAL_OVERRIDES = {
    "Steve McQueen: Wanted Dead or Alive — Season One, Vol. One": ("Wanted Dead or Alive", None),
    "Red Green Show: Stuffed and Mounted": ("The Red Green Show", None),
    "Family Guy: Something, Something, Something Dark Side": ("Family Guy", None),
    "Clint Eastwood: The Enforcer": ("The Enforcer", "movie"),
    "Alien Quadrilogy (Alien / Aliens / Alien 3 / Alien Resurrection)": ("Alien", "movie"),
    "Beverly Hills Cop I, II, III (Box Set)": ("Beverly Hills Cop", "movie"),
    "The Bourne Trilogy": ("The Bourne Identity", "movie"),
    "Rob Zombie Trilogy": ("House of 1000 Corpses", "movie"),
    "Lonesome Dove: The Complete Series (4-Disc)": ("Lonesome Dove", None),
    "The Man with No Name Trilogy": ("The Good, the Bad and the Ugly", "movie"),
    "The Purge: 5-Movie Collection": ("The Purge", "movie"),
}

# These are box sets/compilations with no single real release title --
# no override will find a meaningful match, so they're left without art.
# (Abduction / Killers / Push (3-Movie Set), 270 Classic Cartoons
# (Collection), Pixar Short Films Collection: Volume 1, 15-Film Horror
# Pack (Blu-ray Essentials), 20 Action Movies (4-DVD Pack),
# King of the Hill: any other seasons)

SEASON_PATTERN = re.compile(
    r"\s*[:\-—]\s*(the\s+)?(complete\s+)?(season|seasons|volume|vol\.?)\b.*$",
    re.IGNORECASE,
)
PAREN_PATTERN = re.compile(r"\s*\([^)]*\)\s*$")


def clean_query(title, category):
    if title in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[title]
    cleaned = title
    if category == "tv":
        cleaned = SEASON_PATTERN.sub("", cleaned)
    cleaned = PAREN_PATTERN.sub("", cleaned)
    return (cleaned.strip(), None)


def load_key():
    if not KEY_FILE.exists():
        print(f"Create {KEY_FILE.name} in this folder with your TMDb API key inside, then rerun.")
        raise SystemExit(1)
    return KEY_FILE.read_text().strip()


def search_endpoint(query, endpoint, api_key):
    resp = requests.get(
        f"{BASE_URL}/search/{endpoint}",
        params={"api_key": api_key, "query": query},
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None
    poster_path = results[0].get("poster_path")
    return f"{IMAGE_BASE}{poster_path}" if poster_path else None


def search_poster(query, category, forced_endpoint, api_key):
    primary = forced_endpoint or ("movie" if category == "movie" else "tv")
    fallback = "tv" if primary == "movie" else "movie"

    poster = search_endpoint(query, primary, api_key)
    if poster:
        return poster, primary
    poster = search_endpoint(query, fallback, api_key)
    if poster:
        return poster, fallback
    return None, primary


def main():
    api_key = load_key()
    items = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    for item in items:
        title = item["title"]
        category = item.get("category", "movie")
        query, forced_endpoint = clean_query(title, category)

        try:
            poster, used_endpoint = search_poster(query, category, forced_endpoint, api_key)
        except requests.RequestException as e:
            print(f"  Error looking up {title}: {e}")
            poster = None
            used_endpoint = "?"

        item["poster"] = poster
        note = f" (searched '{query}' as {used_endpoint})" if query != title else ""
        print(f"{title}: {'found' if poster else 'no match'}{note}")

        time.sleep(0.25)  # be polite to the API

    DATA_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nDone. media.json updated with poster URLs.")


if __name__ == "__main__":
    main()
