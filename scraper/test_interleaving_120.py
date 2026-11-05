import json
from collections import Counter, defaultdict
import random
import sys

# Load total_catalog from test_balanced_120
sys.path.append('scraper')
from test_balanced_120 import total_catalog

print(f"Loaded total catalog of {len(total_catalog)} items.")

# Interleaving algorithm:
# We have 120 items: 40 Amazon TR, 40 Hepsiburada, 40 Idefix
# Stores can strictly cycle: Amazon TR -> Hepsiburada -> Idefix -> Amazon TR ... (40 cycles of 3 stores)
# Within each store, we want categories to rotate: Teknoloji -> Moda -> Ev & Yaşam -> Kozmetik -> ...

store_order = ['Amazon TR', 'Hepsiburada', 'Idefix']
items_by_store = {s: [] for s in store_order}
for it in total_catalog:
    items_by_store[it['store']].append(it)

# Organize each store by category
store_cat_items = {}
for s in store_order:
    cats = defaultdict(list)
    for it in items_by_store[s]:
        cats[it['category']].append(it)
    store_cat_items[s] = cats

# Smart picker
def pick_next(store, forbidden_cat, forbidden_ptype):
    cats_dict = store_cat_items[store]
    # Priority: categories that are not forbidden_cat, sorted by largest remaining count
    cands_cats = sorted(
        [c for c in cats_dict if cats_dict[c] and c != forbidden_cat],
        key=lambda c: len(cats_dict[c]),
        reverse=True
    )
    if not cands_cats:
        cands_cats = sorted(
            [c for c in cats_dict if cats_dict[c]],
            key=lambda c: len(cats_dict[c]),
            reverse=True
        )
    if not cands_cats:
        return None
        
    for cat in cands_cats:
        # Prefer item not having forbidden_ptype
        items = cats_dict[cat]
        for idx, it in enumerate(items):
            if it.get('ptype') != forbidden_ptype:
                return items.pop(idx)
        # If none, take first
        return items.pop(0)
    return None

interleaved = []
last_cat = None
last_ptype = None

for round_num in range(40):
    for store in store_order:
        item = pick_next(store, last_cat, last_ptype)
        if item:
            interleaved.append(item)
            last_cat = item.get('category')
            last_ptype = item.get('ptype')

print(f"Total Interleaved: {len(interleaved)}")
print("Store counts:", Counter(x['store'] for x in interleaved))
print("Category counts:", Counter(x['category'] for x in interleaved))

# Check collisions
store_collisions = 0
category_collisions = 0
ptype_collisions = 0

for i in range(len(interleaved) - 1):
    cur = interleaved[i]
    nxt = interleaved[i + 1]
    if cur['store'] == nxt['store']:
        store_collisions += 1
    if cur['category'] == nxt['category']:
        category_collisions += 1
    if cur['ptype'] == nxt['ptype'] and cur['ptype'] != 'diger':
        ptype_collisions += 1

print(f"Store Collisions (consecutive identical stores): {store_collisions}")
print(f"Category Collisions (consecutive identical categories): {category_collisions}")
print(f"PType Collisions (consecutive identical product types): {ptype_collisions}")

# Show sample 15 items in order
print("\n--- First 15 Feed Cards ---")
for idx, x in enumerate(interleaved[:15]):
    print(f"#{idx+1:02d} [{x['store']}] [{x['category']}] ({x['brand']} {x['ptype']}) : {x['title'][:45]} | {x['discountedPrice']} TL (was {x['originalPrice']} TL, -%{x['discountRate']})")
