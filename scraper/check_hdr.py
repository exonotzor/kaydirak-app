import json
from collections import Counter
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('scraper/harvested_deals_raw.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print(f"Total in harvested_deals_raw: {len(d)}")
print("Stores:", dict(Counter(x.get('store') for x in d)))
print("Categories:", dict(Counter(x.get('category') for x in d)))
