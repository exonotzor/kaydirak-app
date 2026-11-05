import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('scraper/hepsiburada_verified_deals.json', 'r', encoding='utf-8') as f:
    hb = json.load(f)

print(f"Total HB deals: {len(hb)}")
hb_cosmetics = []
for x in hb:
    t = x.get('title', '').lower()
    if any(k in t for k in ['krem', 'serum', 'şampuan', 'parfüm', 'parfum', 'maske', 'cilt', 'losyon', 'göz', 'tonik']):
        hb_cosmetics.append(x)
        print(f"HB Cosmetic: {x['title'][:60]} (%{x.get('discountRate')})")
