import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('scraper/final_equal_verified_catalog.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

tech = [x for x in d if x['category'] == 'Teknoloji']
print(f"Total Teknoloji items: {len(tech)}")
for i, x in enumerate(tech):
    print(f"{i+1:2d}. [{x['store']:11s}] %{x['discountRate']:2d} | {x['title']}")
