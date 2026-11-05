import json
from collections import Counter

with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

realistic = [
    it for it in items
    if 50 <= it.get('discountRate', 0) <= 75 and it.get('discountedPrice', 0) >= 60
]

print('Total yaniyo items:', len(items))
print('Realistic (50-75% discount, price >= 60 TL):', len(realistic))
print('By category:', Counter(it['category'] for it in realistic))

for it in realistic[:10]:
    print(f"%{it['discountRate']} | {it['discountedPrice']} TL (was {it['originalPrice']} TL) | {it['title'][:40]}")
