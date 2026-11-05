import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('scraper/hepsiburada_verified_deals.json', 'r', encoding='utf-8') as f:
    hb = json.load(f)

for i, x in enumerate(hb):
    print(f"{i+1:2d}. [{x.get('category')}] %{x.get('discountRate')} | {x.get('title')[:60]}")
