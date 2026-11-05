import json
import re
from collections import Counter
import sys

# Configure stdout encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from test_extractor import extract_brand_and_ptype

# 1. Load pools
with open('scraper/amazon_verified_deals.json', 'r', encoding='utf-8') as f:
    amz_pool = json.load(f)

with open('scraper/hepsiburada_verified_deals.json', 'r', encoding='utf-8') as f:
    hb_pool = json.load(f)

with open('scraper/idefix_strict_onpage.json', 'r', encoding='utf-8') as f:
    idf_strict = json.load(f)
with open('scraper/home_beauty_strict.json', 'r', encoding='utf-8') as f:
    idf_hb = json.load(f)
with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    idf_tech = json.load(f)

idf_pool = idf_strict + idf_hb + idf_tech

for p, name in [(amz_pool, 'Amazon TR'), (hb_pool, 'Hepsiburada'), (idf_pool, 'Idefix')]:
    for item in p:
        item['store'] = name
        b, pt = extract_brand_and_ptype(item['title'])
        item['brand'] = b
        item['ptype'] = pt
        item['brand_type'] = f"{b}_{pt}"

# Global set of seen brand-types
global_seen_brand_types = set()

# Helper to group a pool by category
def group_by_cat(pool):
    cats = {'Teknoloji': [], 'Moda': [], 'Ev & Yaşam': [], 'Kozmetik': []}
    for it in pool:
        c = it.get('category', 'Diğer')
        if c in cats:
            cats[c].append(it)
    for c in cats:
        cats[c].sort(key=lambda x: x.get('discountRate', 0), reverse=True)
    return cats

hb_cats = group_by_cat(hb_pool)
amz_cats = group_by_cat(amz_pool)
idf_cats = group_by_cat(idf_pool)

print("Pool category counts:")
print("HB:", {c: len(items) for c, items in hb_cats.items()})
print("AMZ:", {c: len(items) for c, items in amz_cats.items()})
print("IDF:", {c: len(items) for c, items in idf_cats.items()})

# Selection strategy:
# HB has 41 items total (13 Tek, 12 Moda, 13 Ev, 3 Koz).
# We want exactly 40 HB items. So we pick almost all HB items (40 items).
selected_hb = []
for c in ['Teknoloji', 'Moda', 'Ev & Yaşam', 'Kozmetik']:
    for it in hb_cats[c]:
        bt = it['brand_type']
        if bt not in global_seen_brand_types and len(selected_hb) < 40:
            global_seen_brand_types.add(bt)
            selected_hb.append(it)

print(f"\nSelected HB: {len(selected_hb)}", Counter(x['category'] for x in selected_hb))

# Next, Amazon (we want exactly 40 Amazon items).
# AMZ has ~10 Teknoloji, 10 Moda, 15 Ev & Yaşam, 61 Kozmetik.
# Target: ~8-10 Teknoloji, ~8-10 Moda, ~8-10 Ev & Yaşam, ~12-14 Kozmetik = 40
selected_amz = []
for c, target in [('Teknoloji', 10), ('Moda', 10), ('Ev & Yaşam', 10), ('Kozmetik', 10)]:
    count = 0
    for it in amz_cats[c]:
        bt = it['brand_type']
        if bt not in global_seen_brand_types and count < target:
            global_seen_brand_types.add(bt)
            selected_amz.append(it)
            count += 1

# If Amazon is under 40, fill from Kozmetik / Ev & Yaşam
for c in ['Kozmetik', 'Ev & Yaşam', 'Teknoloji', 'Moda']:
    for it in amz_cats[c]:
        if len(selected_amz) >= 40:
            break
        bt = it['brand_type']
        if bt not in global_seen_brand_types:
            global_seen_brand_types.add(bt)
            selected_amz.append(it)

print(f"Selected Amazon: {len(selected_amz)}", Counter(x['category'] for x in selected_amz))

# Next, Idefix (we want exactly 40 Idefix items).
# We can balance the remaining categories to achieve ~30 each overall!
current_total = Counter(x['category'] for x in selected_hb + selected_amz)
print("Current total before Idefix:", current_total)
# Target total is 30 each:
# Teknoloji needed: 30 - current_total['Teknoloji']
# Moda needed: 30 - current_total['Moda']
# Ev & Yaşam needed: 30 - current_total['Ev & Yaşam']
# Kozmetik needed: 30 - current_total['Kozmetik']

selected_idf = []
for c in ['Teknoloji', 'Moda', 'Ev & Yaşam', 'Kozmetik']:
    needed = 30 - current_total[c]
    count = 0
    for it in idf_cats[c]:
        bt = it['brand_type']
        if bt not in global_seen_brand_types and count < needed:
            global_seen_brand_types.add(bt)
            selected_idf.append(it)
            count += 1

# Fill Idefix up to 40 if needed
for c in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
    for it in idf_cats[c]:
        if len(selected_idf) >= 40:
            break
        bt = it['brand_type']
        if bt not in global_seen_brand_types:
            global_seen_brand_types.add(bt)
            selected_idf.append(it)

print(f"Selected Idefix: {len(selected_idf)}", Counter(x['category'] for x in selected_idf))

total_catalog = selected_amz + selected_hb + selected_idf
print(f"\n=== FINAL CATALOG RESULTS ===")
print(f"Total Products: {len(total_catalog)}")
print("Store Distribution:", Counter(x['store'] for x in total_catalog))
print("Category Distribution:", Counter(x['category'] for x in total_catalog))

# Brand type uniqueness test
bt_counts = Counter(x['brand_type'] for x in total_catalog)
dups = [k for k, v in bt_counts.items() if v > 1]
print(f"Duplicates count: {len(dups)}")
assert len(total_catalog) == 120, "Must be exactly 120 items!"
assert len(selected_amz) == 40, "Amazon must be exactly 40!"
assert len(selected_hb) == 40, "Hepsiburada must be exactly 40!"
assert len(selected_idf) == 40, "Idefix must be exactly 40!"
assert len(dups) == 0, "Brand-types must have 0 duplicates!"
print("[SUCCESS] All constraints satisfied perfectly!")
