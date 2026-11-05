import json

with open('lib/data/live_deals.json', encoding='utf-8') as f:
    deals = json.load(f)

print(f"Total deals: {len(deals)}")
for d in deals:
    if d['store'] != 'Idefix':
        print(f"[{d['store']}] {d['id']} - {d['title']}")
        print(f"   Image: {d['imageUrl']}")
        print(f"   URL:   {d['productUrl']}")
        print(f"   Price: {d['discountedPrice']} TL (was {d['originalPrice']} TL, -%{d['discountRate']})")
