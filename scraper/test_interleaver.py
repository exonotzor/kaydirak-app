import json
from collections import Counter

# Run curation
import sys
sys.path.append('scraper')
from test_curation import amz_curated, hb_curated, idf_curated

queues = {
    'Amazon TR': list(amz_curated),
    'Hepsiburada': list(hb_curated),
    'Idefix': list(idf_curated)
}

store_order = ['Amazon TR', 'Hepsiburada', 'Idefix']
interleaved = []
last_store = None
last_cat = None

while any(len(q) > 0 for q in queues.values()):
    # pick next store that is not last_store
    eligible_stores = [s for s in store_order if s != last_store and len(queues[s]) > 0]
    if not eligible_stores:
        eligible_stores = [s for s in store_order if len(queues[s]) > 0]
    if not eligible_stores:
        break
        
    # pick the store
    chosen_store = eligible_stores[0]
    q = queues[chosen_store]
    
    # find an item with category != last_cat if possible
    chosen_idx = 0
    if last_cat:
        diff_cats = [i for i, item in enumerate(q) if item.get('category') != last_cat]
        if diff_cats:
            chosen_idx = diff_cats[0]
            
    item = q.pop(chosen_idx)
    interleaved.append(item)
    last_store = item['store']
    last_cat = item.get('category')

print(f"Interleaved count: {len(interleaved)}")

# Verify adjacent differences
store_collisions = 0
cat_collisions = 0
for i in range(len(interleaved) - 1):
    if interleaved[i]['store'] == interleaved[i+1]['store']:
        store_collisions += 1
    if interleaved[i].get('category') == interleaved[i+1].get('category'):
        cat_collisions += 1

print(f"Store collisions: {store_collisions}")
print(f"Category collisions: {cat_collisions}")

print("\n--- Card Sequence Preview (First 15 Cards) ---")
for i, it in enumerate(interleaved[:15]):
    print(f"Card {i+1:02d}: [{it['store']:11s}] [{it['category']:10s}] %{it['discountRate']:2d} | {it['discountedPrice']:7.2f} TL | {it['title'][:38]}")
