import json
from collections import Counter
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('scraper/final_verified_catalog.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print(f"Total in final_verified_catalog: {len(d)}")
print("Stores:", dict(Counter(x.get('store') for x in d)))
print("Categories:", dict(Counter(x.get('category') for x in d)))
print("\nFirst 3 items:")
for i, x in enumerate(d[:3]):
    print(f"  {i+1}. [{x.get('store')}] [{x.get('category')}] {x.get('title')[:60]}")
