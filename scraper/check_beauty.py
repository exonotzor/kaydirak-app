import json

with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

beauty = [
    it for it in items
    if it.get('category') == 'Kozmetik' and 50 <= it.get('discountRate', 0) <= 75 and it.get('discountedPrice', 0) >= 40
]

print(f"Kozmetik realistic count: {len(beauty)}")
for b in beauty[:10]:
    print(f"%{b['discountRate']} | {b['discountedPrice']} TL (was {b['originalPrice']} TL) | {b['title'][:40]}")
