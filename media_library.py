"""
media_library.py

A simple command-line tool for browsing and searching your physical
media collection (DVDs, Blu-rays, VHS, TV series), stored as a JSON file.

Usage:
    python media_library.py                # list everything
    python media_library.py search matrix  # search by title (partial match)
    python media_library.py format dvd     # filter by format
    python media_library.py have           # only items you own
    python media_library.py need           # only items on your "need" list
    python media_library.py stats          # quick counts by format/status
"""

import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent / "media.json"


def load_library():
    if not DATA_FILE.exists():
        print(f"Couldn't find {DATA_FILE.name}. Create it first (see media.example.json).")
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def print_item(item):
    status = item.get("status", "have")
    tag = "[NEED]" if status == "need" else "[HAVE]"
    fmt = item.get("format", "?")
    print(f"{tag} {item['title']} ({fmt})")


def cmd_list(items):
    for item in items:
        print_item(item)
    print(f"\n{len(items)} item(s)")


def cmd_search(items, term):
    term = term.lower()
    matches = [i for i in items if term in i["title"].lower()]
    cmd_list(matches)


def cmd_format(items, fmt):
    fmt = fmt.lower()
    matches = [i for i in items if i.get("format", "").lower() == fmt]
    cmd_list(matches)


def cmd_status(items, status):
    matches = [i for i in items if i.get("status", "have") == status]
    cmd_list(matches)


def cmd_stats(items):
    by_format = {}
    by_status = {"have": 0, "need": 0}
    for i in items:
        fmt = i.get("format", "unknown")
        by_format[fmt] = by_format.get(fmt, 0) + 1
        status = i.get("status", "have")
        by_status[status] = by_status.get(status, 0) + 1

    print("By format:")
    for fmt, count in sorted(by_format.items()):
        print(f"  {fmt}: {count}")

    print("\nBy status:")
    for status, count in by_status.items():
        print(f"  {status}: {count}")

    print(f"\nTotal: {len(items)}")


def main():
    items = load_library()
    args = sys.argv[1:]

    if not args:
        cmd_list(items)
    elif args[0] == "search" and len(args) > 1:
        cmd_search(items, " ".join(args[1:]))
    elif args[0] == "format" and len(args) > 1:
        cmd_format(items, args[1])
    elif args[0] == "have":
        cmd_status(items, "have")
    elif args[0] == "need":
        cmd_status(items, "need")
    elif args[0] == "stats":
        cmd_stats(items)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
