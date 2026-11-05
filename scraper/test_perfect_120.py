import json
from collections import Counter, defaultdict
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from test_true_cat import amz_pool, hb_pool, idf_pool

# Target:
# AMZ: 10 Teknoloji, 10 Moda, 10 Ev & Yaşam, 10 Kozmetik = 40
# HB:  13 Teknoloji, 12 Moda, 12 Ev & Yaşam, 3 Kozmetik  = 40
# IDF: 7 Teknoloji,  8 Moda,  8 Ev & Yaşam,  17 Kozmetik = 40
# Total: 30 Teknoloji, 30 Moda, 30 Ev & Yaşam, 30 Kozmetik = 120 total products!

global_seen = set()

# 1. Pick HB (least pool size, so pick first)
hb_by_cat = defaultdict(list)
for x in sorted(hb_pool, key=lambda it: it.get('discountRate', 0), reverse=True):
    hb_by_cat[x['category']].append(x)

selected_hb = []
hb_targets = {'Teknoloji': 13, 'Ev & Yaşam': 12, 'Moda': 12, 'Kozmetik': 3}
for c, target in hb_targets.items():
    count = 0
    for it in hb_by_cat[c]:
        bt = it['brand_type']
        if bt not in global_seen and count < target:
            global_seen.add(bt)
            selected_hb.append(it)
            count += 1

print("Selected HB:", len(selected_hb), Counter(x['category'] for x in selected_hb))

# 2. Pick Amazon (10 each)
amz_by_cat = defaultdict(list)
for x in sorted(amz_pool, key=lambda it: it.get('discountRate', 0), reverse=True):
    amz_by_cat[x['category']].append(x)

selected_amz = []
amz_targets = {'Teknoloji': 10, 'Moda': 10, 'Ev & Yaşam': 10, 'Kozmetik': 10}
for c, target in amz_targets.items():
    count = 0
    for it in amz_by_cat[c]:
        bt = it['brand_type']
        if bt not in global_seen and count < target:
            global_seen.add(bt)
            selected_amz.append(it)
            count += 1

# If any amz cat is short (e.g. Moda might have 9 unique), fill from available
for c in ['Ev & Yaşam', 'Kozmetik', 'Teknoloji', 'Moda']:
    for it in amz_by_cat[c]:
        if len(selected_amz) >= 40:
            break
        bt = it['brand_type']
        if bt not in global_seen:
            global_seen.add(bt)
            selected_amz.append(it)

print("Selected Amazon:", len(selected_amz), Counter(x['category'] for x in selected_amz))

# 3. Pick Idefix to balance exactly to 30 per category
cur_counts = Counter(x['category'] for x in selected_hb + selected_amz)
print("Base counts (HB + AMZ):", cur_counts)

idf_by_cat = defaultdict(list)
for x in sorted(idf_pool, key=lambda it: it.get('discountRate', 0), reverse=True):
    idf_by_cat[x['category']].append(x)

selected_idf = []
for c in ['Teknoloji', 'Moda', 'Ev & Yaşam', 'Kozmetik']:
    needed = 30 - cur_counts[c]
    count = 0
    for it in idf_by_cat[c]:
        bt = it['brand_type']
        if bt not in global_seen and count < needed:
            global_seen.add(bt)
            selected_idf.append(it)
            count += 1

print("Selected Idefix:", len(selected_idf), Counter(x['category'] for x in selected_idf))

total = selected_amz + selected_hb + selected_idf
print("\n=== VERIFICATION OF EQUAL DISTRIBUTION ===")
print("Total Count:", len(total))
print("Stores:", Counter(x['store'] for x in total))
print("Categories:", Counter(x['category'] for x in total))

dups = [k for k, v in Counter(x['brand_type'] for x in total).items() if v > 1]
print("Duplicate (brand, type) pairs:", len(dups))
