import json

with open('scraper/hepsiburada_verified_deals.json', 'r', encoding='utf-8') as f:
    hb = json.load(f)

print(f"Total HB: {len(hb)}")
for i, d in enumerate(hb):
    print(f"{i+1}. [{d['category']}] %{d['discountRate']} | {d['discountedPrice']} TL (was {d['originalPrice']} TL) | {d['title']} | {d['productUrl']}")
