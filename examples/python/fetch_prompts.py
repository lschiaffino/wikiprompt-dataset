#!/usr/bin/env python3
"""Fetch Wikiprompt prompts WITH their full text (content), using an API key.

Get a free key: sign up at wikiprompt.org, then create a key in your profile
(https://www.wikiprompt.org/profile). Pass it via the WIKIPROMPT_API_KEY env var.

Usage:
    WIKIPROMPT_API_KEY=... python3 fetch_prompts.py [out.ndjson] [category]
"""
import json
import os
import sys
import urllib.request

BASE = "https://www.wikiprompt.org"
KEY = os.environ.get("WIKIPROMPT_API_KEY")
OUT = sys.argv[1] if len(sys.argv) > 1 else "wikiprompt_prompts.ndjson"
CATEGORY = sys.argv[2] if len(sys.argv) > 2 else None

if not KEY:
    sys.exit("Set WIKIPROMPT_API_KEY (create one at https://www.wikiprompt.org/profile)")


def get(page):
    q = f"?page={page}&limit=100" + (f"&category={CATEGORY}" if CATEGORY else "")
    req = urllib.request.Request(
        f"{BASE}/api/v1/prompts{q}",
        headers={"Authorization": f"Bearer {KEY}", "User-Agent": "wikiprompt-api-example"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    page, total_seen = 1, 0
    with open(OUT, "w", encoding="utf-8") as f:
        while page:
            data = get(page)
            for p in data.get("prompts", []):
                # p includes: id, slug, url, title, description, content, category,
                # tags, media_urls, metadata, created_at, ...
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
                total_seen += 1
            print(f"  page {data.get('page')} / total {data.get('total')} -> {total_seen}", flush=True)
            page = data.get("next_page")  # None -> stop
    print(f"done: {total_seen} prompts (with content) -> {OUT}")
    print("Attribution: cite wikiprompt.org; prompt bodies belong to their original authors.")


if __name__ == "__main__":
    main()
