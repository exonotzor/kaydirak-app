import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

for fname in ['top_home_strict.json', 'all_home_strict.json']:
    with open(f'scraper/{fname}', 'r', encoding='utf-8') as f:
        d = json.load(f)
    print(f"{fname}: {len(d)} items, Stores: {set(x.get('store') for x in d)}")
    if d:
        print(f"  Sample: {d[0]['title'][:50]}")
