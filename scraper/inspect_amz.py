import json
from collections import Counter

with open('scraper/amazon_verified_deals.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total Amazon deals: {len(data)}")
print(Counter(x['category'] for x in data))

for cat in ['Teknoloji', 'Moda', 'Ev & Yaşam', 'Kozmetik']:
    items = [x for x in data if x['category'] == cat]
    print(f"\n--- {cat} ({len(items)}) ---")
    for it in items[:4]:
        print(f"  %{it['discountRate']} | {it['discountedPrice']} TL (was {it['originalPrice']} TL) | {it['title'][:40]} | {it['productUrl']}")
