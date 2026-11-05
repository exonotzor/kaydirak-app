import json
import re
from collections import Counter
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

print(f"Pool sizes: Amazon={len(amz_pool)}, HB={len(hb_pool)}, Idefix={len(idf_pool)}")

# Tag all items with (brand, ptype)
for p, name in [(amz_pool, 'Amazon TR'), (hb_pool, 'Hepsiburada'), (idf_pool, 'Idefix')]:
    for item in p:
        item['store'] = name
        b, pt = extract_brand_and_ptype(item['title'])
        item['brand'] = b
        item['ptype'] = pt
        item['brand_type'] = f"{b}_{pt}"

# Global deduplication selection
# We need:
# - Exactly 40 Amazon TR
# - Exactly 40 Hepsiburada
# - Exactly 40 Idefix
# And NO duplicate brand_type across the entire 120 items!

# First, since HB pool has 41 items, pick 40 from HB first.
global_seen_brand_types = set()

selected_hb = []
for item in hb_pool:
    bt = item['brand_type']
    if bt not in global_seen_brand_types:
        global_seen_brand_types.add(bt)
        selected_hb.append(item)
        if len(selected_hb) >= 40:
            break

print(f"Selected HB: {len(selected_hb)}")

# Next, pick 40 from Amazon TR
selected_amz = []
# Sort Amazon by discount rate descending
amz_sorted = sorted(amz_pool, key=lambda x: x.get('discountRate', 0), reverse=True)
for item in amz_sorted:
    bt = item['brand_type']
    if bt not in global_seen_brand_types:
        global_seen_brand_types.add(bt)
        selected_amz.append(item)
        if len(selected_amz) >= 40:
            break

print(f"Selected Amazon: {len(selected_amz)}")

# Next, pick 40 from Idefix
selected_idf = []
idf_sorted = sorted(idf_pool, key=lambda x: x.get('discountRate', 0), reverse=True)
for item in idf_sorted:
    bt = item['brand_type']
    if bt not in global_seen_brand_types:
        global_seen_brand_types.add(bt)
        selected_idf.append(item)
        if len(selected_idf) >= 40:
            break

print(f"Selected Idefix: {len(selected_idf)}")

total_selected = selected_amz + selected_hb + selected_idf
print(f"\nTotal Selected: {len(total_selected)}")
print("Store counts:", Counter(x['store'] for x in total_selected))
print("Category counts:", Counter(x['category'] for x in total_selected))

# Verify brand_type uniqueness
brand_type_counts = Counter(x['brand_type'] for x in total_selected)
duplicates = [k for k, v in brand_type_counts.items() if v > 1]
print(f"Duplicate brand-types in full 120 catalog: {len(duplicates)}")
if duplicates:
    print("Duplicates found:", duplicates)
else:
    print("✅ PERFECT: 100% of all 120 products have completely unique brand-types!")
