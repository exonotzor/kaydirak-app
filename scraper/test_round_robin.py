import json
from collections import Counter
import sys
sys.path.append('scraper')
from test_curation import amz_curated, hb_curated, idf_curated

def organize_by_category(items):
    by_cat = {}
    for it in items:
        cat = it.get('category', 'Diğer')
        by_cat.setdefault(cat, []).append(it)
    for cat in by_cat:
        by_cat[cat].sort(key=lambda x: x.get('discountRate', 0), reverse=True)
    return by_cat

amz_cats = organize_by_category(amz_curated)
hb_cats = organize_by_category(hb_curated)
idf_cats = organize_by_category(idf_curated)

def pick_item(cat_dict, exclude_cat):
    # First priority: categories that have the most items left, but != exclude_cat
    sorted_cats = sorted(
        [c for c, items in cat_dict.items() if len(items) > 0 and c != exclude_cat],
        key=lambda c: len(cat_dict[c]),
        reverse=True
    )
    if sorted_cats:
        return cat_dict[sorted_cats[0]].pop(0)
    # If only exclude_cat is left, return it
    for c, items in cat_dict.items():
        if len(items) > 0:
            return items.pop(0)
    return None

interleaved = []
last_cat = None
store_order = ['Amazon TR', 'Hepsiburada', 'Idefix']
store_dicts = {
    'Amazon TR': amz_cats,
    'Hepsiburada': hb_cats,
    'Idefix': idf_cats
}

for round_num in range(20):
    for store in store_order:
        item = pick_item(store_dicts[store], last_cat)
        if item:
            item['store'] = store
            interleaved.append(item)
            last_cat = item.get('category')

print(f"Total items: {len(interleaved)}")
print("Store counts:", Counter(x['store'] for x in interleaved))
print("Category counts:", Counter(x['category'] for x in interleaved))

store_collisions = 0
cat_collisions = 0
for i in range(len(interleaved) - 1):
    if interleaved[i]['store'] == interleaved[i+1]['store']:
        store_collisions += 1
    if interleaved[i].get('category') == interleaved[i+1].get('category'):
        cat_collisions += 1

print(f"Store collisions: {store_collisions}")
print(f"Category collisions: {cat_collisions}")

print("\n--- Card Sequence (First 25 Cards) ---")
for i, it in enumerate(interleaved[:25]):
    print(f"Card {i+1:02d}: [{it['store']:11s}] [{it['category']:10s}] %{it['discountRate']:2d} | {it['discountedPrice']:7.2f} TL | {it['title'][:38]}")
