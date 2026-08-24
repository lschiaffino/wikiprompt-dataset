#!/usr/bin/env python3
"""Weekly LLM-benchmarks snapshot for wikiprompt.org/benchmarks.

Pulls open leaderboard data and upserts a dated snapshot into the public
benchmark_scores table, so ranking history accumulates on the record.

Sources (open, attributed on the page):
  - LMArena leaderboard dataset (lmarena-ai/leaderboard-dataset on HF): Elo,
    confidence intervals, votes, rank, license, org for 10 arenas.
  - OpenRouter public models API: pricing, context window, knowledge cutoff.

Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY.
Runs Sundays via GitHub Actions (see .github/workflows/benchmarks.yml);
wikiprompt's daily import also snapshots on weekdays. Idempotent per day.
"""
import json, os, io, math, datetime
import requests
import pyarrow.parquet as pq

SUPA = os.environ['SUPABASE_URL'].rstrip('/')
SVC = os.environ['SUPABASE_SERVICE_ROLE_KEY']
TODAY = datetime.date.today().isoformat()
CONFIGS = ['text', 'webdev', 'vision', 'text_to_image', 'image_edit',
           'text_to_video', 'video_edit', 'search', 'agent', 'document']

def clean(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v

def to_int(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    return int(v)

def upsert(records):
    ok = 0
    for i in range(0, len(records), 500):
        chunk = records[i:i + 500]
        r = requests.post(
            f"{SUPA}/rest/v1/benchmark_scores?on_conflict=source,category,model_name,snapshot_date",
            headers={'apikey': SVC, 'Authorization': f'Bearer {SVC}',
                     'Content-Type': 'application/json',
                     'Prefer': 'resolution=merge-duplicates,return=minimal'},
            data=json.dumps(chunk), timeout=90)
        if r.status_code in (200, 201, 204):
            ok += len(chunk)
        else:
            print(f'  upsert chunk {i}: HTTP {r.status_code} {r.text[:120]}')
    return ok

def main():
    total = 0
    for cfg in CONFIGS:
        url = (f"https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/"
               f"resolve/main/{cfg}/latest-00000-of-00001.parquet")
        try:
            resp = requests.get(url, timeout=120)
            rows = pq.read_table(io.BytesIO(resp.content)).to_pylist()
        except Exception as e:
            print(f'{cfg}: fetch/parse failed: {e}')
            continue
        best = {}
        for r in rows:
            if not r.get('model_name'):
                continue
            rec = {
                'source': 'lmarena',
                'category': f"{cfg}:{r.get('category') or 'overall'}",
                'model_name': str(r['model_name'])[:120],
                'organization': (r.get('organization') or '')[:80] or None,
                'license': (r.get('license') or '')[:80] or None,
                'score': clean(r.get('rating')),
                'score_lower': clean(r.get('rating_lower')),
                'score_upper': clean(r.get('rating_upper')),
                'votes': to_int(r.get('vote_count')),
                'rank': to_int(r.get('rank')),
                'snapshot_date': TODAY,
                'extra': {'publish_date': r.get('leaderboard_publish_date')},
            }
            k = (rec['category'], rec['model_name'])
            if k not in best or (rec['votes'] or 0) > (best[k]['votes'] or 0):
                best[k] = rec
        n = upsert(list(best.values()))
        total += n
        print(f'lmarena/{cfg}: {len(rows)} rows -> {n}')

    models = requests.get('https://openrouter.ai/api/v1/models', timeout=60).json().get('data', [])
    recs = []
    for m in models:
        pricing = m.get('pricing') or {}
        recs.append({
            'source': 'openrouter', 'category': 'models',
            'model_name': (m.get('name') or m.get('id') or '')[:120],
            'organization': (m.get('id') or '').split('/')[0][:80] or None,
            'license': None, 'score': None, 'rank': None,
            'snapshot_date': TODAY,
            'extra': {'id': m.get('id'), 'context_length': m.get('context_length'),
                      'prompt_price': pricing.get('prompt'),
                      'completion_price': pricing.get('completion'),
                      'knowledge_cutoff': m.get('knowledge_cutoff')},
        })
    total += upsert(recs)
    print(f'openrouter: {len(models)} models')
    print(f'DONE total={total} snapshot={TODAY}')

if __name__ == '__main__':
    main()
