import json
import collections

hb = json.load(open('scraper/hepsiburada_verified_deals.json', encoding='utf-8'))
print('Total HB:', len(hb))
print('Categories:', collections.Counter(x['category'] for x in hb))
for x in hb:
    b = x.get('brand', '')
    p = x.get('ptype', '')
    t = x.get('title', '')[:40]
    dp = x.get('discountedPrice', 0)
    op = x.get('originalPrice', 0)
    c = x.get('category', '')
    print(f"[{c}] {b} {p} : {t} | {dp} TL (was {op} TL)")
