import json

with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

home = [
    it for it in items
    if it.get('category') == 'Ev & Yaşam' and 50 <= it.get('discountRate', 0) <= 75 and it.get('discountedPrice', 0) >= 60
]

print(f"Ev & Yaşam realistic count: {len(home)}")
for h in home[:10]:
    print(f"%{h['discountRate']} | {h['discountedPrice']} TL (was {h['originalPrice']} TL) | {h['title'][:40]}")
