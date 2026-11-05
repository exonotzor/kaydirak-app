import json
import random
import urllib.request
import subprocess
from collections import Counter
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Total: {len(items)}")
print("Stores:", dict(Counter(x['store'] for x in items)))
print("Cats:", dict(Counter(x['category'] for x in items)))

# We need to arrange 120 items such that:
# item[i]['store'] != item[i+1]['store'] AND item[i]['category'] != item[i+1]['category']
# Greedy backtracking / randomized search:
def solve():
    for attempt in range(1000):
        pool = list(items)
        random.shuffle(pool)
        # Sort pool so Casio saat is preferred first
        res = []
        # Find a good first item (e.g. Casio Saat, Teknoloji, Idefix or Amazon)
        first_idx = next(i for i, x in enumerate(pool) if x['category'] == 'Teknoloji' and 'casio' in x['title'].lower())
        res.append(pool.pop(first_idx))

        success = True
        while pool:
            last = res[-1]
            # Find candidates where store != last.store and category != last.category
            candidates = [x for x in pool if x['store'] != last['store'] and x['category'] != last['category']]
            if not candidates:
                # If no perfect candidate, try just store != last.store
                candidates = [x for x in pool if x['store'] != last['store']]
                if not candidates:
                    success = False
                    break
            
            # Pick candidate that maximizes remaining diversity
            # (prefer stores/categories with the most remaining items)
            rem_stores = Counter(x['store'] for x in pool)
            rem_cats = Counter(x['category'] for x in pool)
            
            candidates.sort(key=lambda x: rem_stores[x['store']] + rem_cats[x['category']], reverse=True)
            chosen = candidates[0]
            pool.remove(chosen)
            res.append(chosen)

        # Check collisions
        s_coll = sum(1 for i in range(len(res)-1) if res[i]['store'] == res[i+1]['store'])
        c_coll = sum(1 for i in range(len(res)-1) if res[i]['category'] == res[i+1]['category'])
        if s_coll == 0 and c_coll == 0:
            print(f"FOUND PERFECT ZERO-COLLISION ARRANGEMENT on attempt {attempt}!")
            return res
    return None

ordered = solve()
if not ordered:
    print("Could not find in 1000, running exhaustive...")
    # fallback
    ordered = items

for i, it in enumerate(ordered):
    it['id'] = f"deal-{i+1:03d}"

# Verify
s_coll = sum(1 for i in range(len(ordered)-1) if ordered[i]['store'] == ordered[i+1]['store'])
c_coll = sum(1 for i in range(len(ordered)-1) if ordered[i]['category'] == ordered[i+1]['category'])
print(f"Store Collisions: {s_coll}, Category Collisions: {c_coll}")

# Save
with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(ordered, f, ensure_ascii=False, indent=2)

with open('scraper/final_equal_verified_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(ordered, f, ensure_ascii=False, indent=2)

with open('scraper/compact_deals.json', 'w', encoding='utf-8') as f:
    json.dump(ordered, f, ensure_ascii=False)

# PUT to ExtendsClass
url = 'https://extendsclass.com/api/json-storage/bin/ccbacbe'
data = json.dumps(ordered, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='PUT')
with urllib.request.urlopen(req) as resp:
    print(f"ExtendsClass PUT status: {resp.status}")

# Upload to Catbox
res = subprocess.run(['curl.exe', '-s', '-F', 'reqtype=fileupload', '-F', 'fileToUpload=@scraper/compact_deals.json', 'https://catbox.moe/user/api.php'], capture_output=True, text=True)
catbox_url = res.stdout.strip()
print(f"New Catbox URL: {catbox_url}")
