import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('scraper/final_equal_verified_catalog.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for cat in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
    items = [x for x in d if x['category'] == cat]
    print(f"\n=== Current {cat} (Top 5) ===")
    for i, it in enumerate(items[:5]):
        print(f"  {i+1}. [{it['store']}] %{it['discountRate']} | {it['title'][:60]}")
