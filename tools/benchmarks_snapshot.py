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
import json, os, io, re, csv, math, datetime
import requests
import yaml
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

def fetch_livebench():
    """LiveBench: table_{release}.csv; releases baked into the JS bundle."""
    home = requests.get('https://livebench.ai/', timeout=30).text
    m = re.search(r'src="(\./static/js/main[^"]+\.js)"', home)
    if not m: return []
    bundle = requests.get('https://livebench.ai/' + m.group(1).lstrip('./'), timeout=60).text
    dates = sorted(set(re.findall(r'"(20\d{2}-\d{2}-\d{2})"', bundle)), reverse=True)[:12]
    for d in dates:
        r = requests.get(f"https://livebench.ai/table_{d.replace('-', '_')}.csv", timeout=30)
        if r.status_code != 200 or not r.text.startswith('model'): continue
        rows = list(csv.DictReader(io.StringIO(r.text)))
        scored = []
        for row in rows:
            vals = [float(v) for k, v in row.items() if k != 'model' and v not in ('', None)]
            if vals: scored.append((row['model'], sum(vals) / len(vals)))
        scored.sort(key=lambda x: -x[1])
        return [{'source': 'livebench', 'category': 'livebench:overall', 'model_name': mo[:120],
                 'organization': None, 'license': None, 'score': round(a, 2), 'score_lower': None,
                 'score_upper': None, 'votes': None, 'rank': i + 1, 'snapshot_date': TODAY,
                 'extra': {'release': d, 'metric': 'average of category scores (0-100)'}}
                for i, (mo, a) in enumerate(scored)]
    return []

def fetch_benchlm():
    d = requests.get('https://benchlm.ai/data/leaderboard.json', timeout=40).json()
    recs = []
    for r in d.get('items') or []:
        try: score = float(r['displayScore']) if r.get('displayScore') not in (None, '', 'None') else None
        except Exception: score = None
        try: rank = int(r['rank']) if r.get('rank') not in (None, '', 'None') else None
        except Exception: rank = None
        name = str(r.get('model') or r.get('slug') or '')[:120]
        if not name: continue
        recs.append({'source': 'benchlm', 'category': 'benchlm:overall', 'model_name': name,
                     'organization': (r.get('creator') or '')[:80] or None,
                     'license': (r.get('sourceType') or '')[:80] or None,
                     'score': score, 'score_lower': None, 'score_upper': None, 'votes': None,
                     'rank': rank, 'snapshot_date': TODAY,
                     'extra': {'context_window': r.get('contextWindow'), 'metric': 'BenchLM aggregated display score'}})
    return recs

def fetch_aider():
    raw = requests.get('https://raw.githubusercontent.com/Aider-AI/aider/main/aider/website/_data/polyglot_leaderboard.yml', timeout=40).text
    best = {}
    for r in yaml.safe_load(raw) or []:
        model = str(r.get('model') or '')[:120]
        try: rate = float(r.get('pass_rate_2'))
        except Exception: continue
        if model and (model not in best or rate > best[model][0]):
            best[model] = (rate, r.get('edit_format'), r.get('total_cost'))
    ranked = sorted(best.items(), key=lambda kv: -kv[1][0])
    return [{'source': 'aider', 'category': 'aider:polyglot', 'model_name': m, 'organization': None,
             'license': None, 'score': rate, 'score_lower': None, 'score_upper': None, 'votes': None,
             'rank': i + 1, 'snapshot_date': TODAY,
             'extra': {'edit_format': fmt, 'total_cost_usd': cost, 'metric': 'polyglot pass rate 2 (%)'}}
            for i, (m, (rate, fmt, cost)) in enumerate(ranked)]

def extra_sources():
    total = 0
    for name, fn in (('livebench', fetch_livebench), ('benchlm', fetch_benchlm), ('aider', fetch_aider)):
        try: recs = fn()
        except Exception as e:
            print(f'{name}: failed {e}'); continue
        n = upsert(recs)
        total += n
        print(f'{name}: {len(recs)} -> {n}')
    return total

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

    total += extra_sources()

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
