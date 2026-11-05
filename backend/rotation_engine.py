import json
import os
import sys
import re
import random
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(PROJECT_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

STORES = ['Amazon TR', 'Hepsiburada', 'Idefix']
CATEGORIES = ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']
COOLDOWN_RUNS = 8  # Guaranteed no repeats across 8 consecutive runs (~960 items cooldown)
POOL_REFRESH_INTERVAL_SEC = 48 * 3600  # 2 days (48 hours) automatic 1,330-item master pool refresh

# Load / Initialize Rotation State
state_path = os.path.join('backend', 'rotation_state.json')
if os.path.exists(state_path):
    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)
else:
    state = {
        'rotation_count': 0,
        'last_rotation_timestamp': None,
        'last_pool_refresh_epoch': time.time(),
        'last_pool_refresh_timestamp': datetime.now(timezone.utc).isoformat(),
        'history': []
    }

now_epoch = time.time()
last_pool_epoch = float(state.get('last_pool_refresh_epoch') or 0)
if last_pool_epoch == 0:
    state['last_pool_refresh_epoch'] = now_epoch
    state['last_pool_refresh_timestamp'] = datetime.now(timezone.utc).isoformat()
elif (now_epoch - last_pool_epoch) >= POOL_REFRESH_INTERVAL_SEC:
    hours_elapsed = (now_epoch - last_pool_epoch) / 3600.0
    print(f"\n[2-DAY SCHEDULE] {hours_elapsed:.1f} hours since last master pool refresh (>= 48h). Refreshing 1,330-item master pools...")
    try:
        from backend.refresh_master_pools import refresh_all_master_pools
        refresh_all_master_pools()
        state['last_pool_refresh_epoch'] = time.time()
        state['last_pool_refresh_timestamp'] = datetime.now(timezone.utc).isoformat()
    except Exception as e:
        print(f"[2-DAY SCHEDULE WARNING] Master pool refresh encountered an error, continuing with existing verified pools: {e}")

# Load Pools
def load_pool(store_name, filename):
    path = os.path.join('backend', 'pool', filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Pool file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

pool_amazon = load_pool('Amazon TR', 'pool_amazon.json')
pool_hb = load_pool('Hepsiburada', 'pool_hepsiburada.json')
pool_idefix = load_pool('Idefix', 'pool_idefix.json')

pools = {
    'Amazon TR': pool_amazon,
    'Hepsiburada': pool_hb,
    'Idefix': pool_idefix
}

rotation_idx = state.get('rotation_count', 0) + 1
history = state.get('history', [])

# Flatten recent IDs for cooldown
recent_ids = set()
for past_batch in history[-COOLDOWN_RUNS:]:
    for pid in past_batch:
        recent_ids.add(pid)

print(f"=== ROTATION ENGINE #{rotation_idx} (SUB-CATEGORY DIVERSE MODE) ===")
print(f"Active Cooldown IDs from last {COOLDOWN_RUNS} runs: {len(recent_ids)}")

# Build recency lookup: how many runs ago was item shown?
last_seen_run = {}
for run_num, batch in enumerate(history, 1):
    for pid in batch:
        last_seen_run[pid] = run_num

def select_diverse_10(candidates):
    """
    Picks 10 items by round-robin sampling across subCategory buckets
    so that no single sub-category dominates the selection.
    """
    buckets = defaultdict(list)
    for it in candidates:
        subcat = it.get('subCategory') or 'Genel'
        buckets[subcat].append(it)

    subcat_keys = list(buckets.keys())
    random.shuffle(subcat_keys)
    for k in subcat_keys:
        # Prioritize never-shown items first, but randomize within same recency tier
        never = [x for x in buckets[k] if x['id'] not in last_seen_run]
        seen = [x for x in buckets[k] if x['id'] in last_seen_run]
        random.shuffle(never)
        seen.sort(key=lambda x: last_seen_run.get(x['id'], 0))
        buckets[k] = never + seen

    chosen = []
    while len(chosen) < 10:
        added_in_round = False
        for k in subcat_keys:
            if buckets[k]:
                chosen.append(buckets[k].pop(0))
                added_in_round = True
                if len(chosen) == 10:
                    break
        if not added_in_round:
            break
    return chosen

# Select 10 items for each of the 12 bins
selected_by_bin = {}
new_batch_ids = []

for store in STORES:
    for cat in CATEGORIES:
        available = pools[store].get(cat, [])
        if not available:
            raise ValueError(f"Pool empty for {store} - {cat}!")

        # Eligible candidates outside cooldown
        eligible = [it for it in available if it['id'] not in recent_ids]
        if len(eligible) < 10:
            in_cooldown = [it for it in available if it['id'] in recent_ids]
            in_cooldown.sort(key=lambda x: last_seen_run.get(x['id'], 0))
            eligible.extend(in_cooldown)

        chosen = select_diverse_10(eligible)
        if len(chosen) < 10:
            raise ValueError(f"Insufficient items in {store} - {cat}: available {len(chosen)}/10")

        selected_by_bin[(store, cat)] = list(chosen)
        for it in chosen:
            new_batch_ids.append(it['id'])

        fresh_count = sum(1 for it in chosen if it['id'] not in recent_ids)
        subcats_used = len(set(it.get('subCategory', 'Genel') for it in chosen))
        print(f"[{store:11}] [{cat:10}] Selected 10 items ({fresh_count}/10 fresh, across {subcats_used} sub-categories)")

all_120 = [it for bin_items in selected_by_bin.values() for it in bin_items]
assert len(all_120) == 120

c_store = Counter(it['store'] for it in all_120)
c_cat = Counter(it['category'] for it in all_120)
print(f"\nStore balance: {dict(c_store)}")
print(f"Category balance: {dict(c_cat)}")
assert c_store['Amazon TR'] == 40 and c_store['Hepsiburada'] == 40 and c_store['Idefix'] == 40
assert c_cat['Teknoloji'] == 30 and c_cat['Moda'] == 30 and c_cat['Kozmetik'] == 30 and c_cat['Ev & Yaşam'] == 30

# Interleaving Solver (0 Store Collisions, 0 Category Collisions)
bins_copy = {k: list(v) for k, v in selected_by_bin.items()}

def solve_order(seq, remaining):
    if len(seq) == 120:
        return seq
    last_s = seq[-1]['store'] if seq else None
    last_c = seq[-1]['category'] if seq else None

    candidates = []
    for (s, c), items in remaining.items():
        if len(items) > 0 and s != last_s and c != last_c:
            candidates.append(((s, c), len(items)))
    candidates.sort(key=lambda x: -x[1])

    for (s, c), _ in candidates:
        it = remaining[(s, c)].pop()
        seq.append(it)
        res = solve_order(seq, remaining)
        if res is not None:
            return res
        seq.pop()
        remaining[(s, c)].append(it)
    return None

ordered = solve_order([], bins_copy)
assert ordered is not None and len(ordered) == 120

store_cols = sum(1 for i in range(119) if ordered[i]['store'] == ordered[i+1]['store'])
cat_cols = sum(1 for i in range(119) if ordered[i]['category'] == ordered[i+1]['category'])
print(f"Store collisions: {store_cols}, Category collisions: {cat_cols}")
assert store_cols == 0 and cat_cols == 0

# Clean compact catalog for Flutter app with safe size limits
compact_catalog = []
for it in ordered:
    title = str(it.get('title', '')).strip()[:100]
    img = str(it.get('imageUrl', '')).strip()
    if len(img) > 200:
        m = re.search(r'(https://[^\s\"\'\\]+\.(?:jpg|jpeg|png))', img)
        img = m.group(1) if m else img[:150]

    compact_catalog.append({
        'id': str(it.get('id', '')),
        'title': title,
        'originalPrice': round(float(it.get('originalPrice', 0)), 2),
        'discountedPrice': round(float(it.get('discountedPrice', 0)), 2),
        'discountRate': int(it.get('discountRate', 0)),
        'imageUrl': img,
        'productUrl': str(it.get('productUrl', '')).strip(),
        'store': str(it.get('store', '')).strip(),
        'category': str(it.get('category', '')).strip()
    })

# Save locally to assets
with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(compact_catalog, f, ensure_ascii=False, indent=2)

# Upload to ExtendsClass REST API
endpoint = "https://extendsclass.com/api/json-storage/bin/ccbacbe"
payload = json.dumps(compact_catalog, ensure_ascii=False).encode('utf-8')
print(f"Clean payload size: {len(payload) / 1024:.1f} KB")

req = urllib.request.Request(
    endpoint,
    data=payload,
    headers={
        'Content-Type': 'application/json',
        'User-Agent': f'KaydirakRotationEngine/3.0 (Batch-{rotation_idx})'
    },
    method='PUT'
)

with urllib.request.urlopen(req, timeout=15) as resp:
    print(f"ExtendsClass PUT HTTP status: {resp.status}")
    assert resp.status == 200

# Update Rotation State
state['rotation_count'] = rotation_idx
state['last_rotation_timestamp'] = datetime.now(timezone.utc).isoformat()
state['history'].append(new_batch_ids)
if len(state['history']) > 25:
    state['history'] = state['history'][-25:]

with open(state_path, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print(f"\nSUCCESS! Rotation #{rotation_idx} completed & deployed.")
print(f"120 unique balanced deals live on {endpoint}")
