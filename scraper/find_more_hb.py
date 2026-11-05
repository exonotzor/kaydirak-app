import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

for fname in ['harvested_deals_raw.json', 'final_verified_catalog.json']:
    with open(f'scraper/{fname}', 'r', encoding='utf-8') as f:
        data = json.load(f)
    hb_items = [x for x in data if x.get('store') == 'Hepsiburada']
    print(f"{fname}: {len(hb_items)} HB items")
    for x in hb_items:
        t = x.get('title', '').lower()
        if any(k in t for k in ['krem', 'serum', 'şampuan', 'parfüm', 'parfum', 'loreal', 'nivea', 'garnier', 'cilt', 'bakım', 'losyon']):
            if not any(k in t for k in ['mont', 'ceket', 'hamam', 'tıraş']):
                print(f"  -> {x['title'][:60]} (%{x.get('discountRate')})")
