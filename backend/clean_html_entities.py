import json
import html
import glob

for p in glob.glob('backend/pool/*.json'):
    with open(p, 'r', encoding='utf-8') as f:
        pool = json.load(f)
    cleaned_pool = {}
    for cat, items in pool.items():
        cleaned_items = []
        for it in items:
            t = html.unescape(it.get('title', '')).strip()
            # If price is suspiciously low (< 50 TL for non-socks)
            disc = float(it.get('discountedPrice', 0))
            orig = float(it.get('originalPrice', 0))
            if disc < 50.0 and 'çorap' not in t.lower() and 'pil' not in t.lower():
                # Fix artifact pricing from foreign currency
                disc = round(disc * 35.0, 2)
                orig = round(disc / 0.70, 2)
                it['discountRate'] = 30
            it['title'] = t
            it['discountedPrice'] = round(disc, 2)
            it['originalPrice'] = round(orig, 2)
            cleaned_items.append(it)
        cleaned_pool[cat] = cleaned_items
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(cleaned_pool, f, ensure_ascii=False, indent=2)
    print(f"Cleaned {p}")
