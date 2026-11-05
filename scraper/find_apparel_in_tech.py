import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

apparel_brands = ['the north face', 'jack wolfskin', 'adidas', 'puma', 'nike', 'benetton', 'madmext', 'tommy', 'columbia', 'under armour', 'millet', 'vogue', 'defacto', 'koton', 'mavi', 'loft', 'avva']

polluted = []
for i, d in enumerate(deals):
    if d['category'] == 'Teknoloji':
        t = d['title'].lower()
        if any(b in t for b in apparel_brands):
            polluted.append((i, d['title'], d['store']))

print(f"Polluted items in Teknoloji: {len(polluted)}")
for p in polluted:
    print(f"Index {p[0]}: [{p[2]}] {p[1]}")
