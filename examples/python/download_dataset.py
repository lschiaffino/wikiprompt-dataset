#!/usr/bin/env python3
"""Download the whole Wikiprompt metadata dataset to a local NDJSON file.

No API key needed - the /dataset endpoint is public (metadata only; the prompt
body is not included - use fetch_prompts.py with an API key for content).

Usage:  python3 download_dataset.py [out.ndjson]
"""
import json
import sys
import urllib.request

BASE = "https://www.wikiprompt.org"
OUT = sys.argv[1] if len(sys.argv) > 1 else "wikiprompt_dataset.ndjson"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "wikiprompt-dataset-example"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    url = f"{BASE}/dataset?limit=500"
    total_seen = 0
    with open(OUT, "w", encoding="utf-8") as f:
        while url:
            page = get(url)
            for rec in page.get("data", []):
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                total_seen += 1
            if "total_prompts" in page:  # page 1 also carries the manifest
                print(f"catalog total: {page['total_prompts']}")
            print(f"  ...{total_seen} records", flush=True)
            url = page.get("next")  # None -> stop
    print(f"done: {total_seen} records -> {OUT}")


if __name__ == "__main__":
    main()
