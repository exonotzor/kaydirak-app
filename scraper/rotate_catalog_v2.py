import json
import os
import random
import urllib.request
import subprocess
from collections import Counter
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(PROJECT_DIR)

# 1. Load current catalog to know what was in top positions
with open('scraper/final_equal_verified_catalog.json', 'r', encoding='utf-8') as f:
    current_catalog = json.load(f)

current_titles = set(x['title'].strip().lower() for x in current_catalog[:30])

# 2. Gather candidates from all available pools
all_pools = []
for p in ['amazon_verified_deals.json', 'hepsiburada_verified_deals.json', 'all_tech_verified.json', 'home_beauty_strict.json', 'yaniyo_amazon_deals.json']:
    path = os.path.join('scraper', p)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                all_pools.extend(data)

print(f"Total raw candidates in pools: {len(all_pools)}")

# Clean and categorize candidate items strictly
def get_clean_cat(it):
    title = it.get('title', '').strip()
    title_lower = title.lower()
    cat = it.get('category', '').strip()

    # Cosmetic check
    if any(k in title_lower for k in ['krem', 'serum', 'losyon', 'nemlendirici', 'hydro boost', 'nivea', 'neutrogena', 'loreal', 'parfüm', 'parfum', 'deodorant', 'şampuan', 'sampuan', 'maske', 'makyaj', 'ruj', 'rimel', 'maskara', 'cilt', 'bakım yağı', 'tonik', 'güneş kremi', 'skinmaster', 'yüz temizleme', 'dudak', 'kolonya']):
        return 'Kozmetik'

    # Fashion check
    if any(k in title_lower for k in ['yelek', 'mont', 'şort', 'sort', 'kapri', 'pantolon', 't-shirt', 'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı', 'bot', 'çorap', 'ceket', 'gömlek', 'polar', 'tayt', 'içlik', 'boxer', 'kaban', 'atlet', 'elbise', 'etek', 'benetton', 'puma', 'nike', 'skechers']):
        return 'Moda'

    # Home check
    if any(k in title_lower for k in ['buzluk', 'termos', 'fincan', 'tava', 'tencere', 'tabak', 'nevresim', 'yastık', 'yorgan', 'havlu', 'deterjan', 'yumuşatıcı', 'sabun', 'cooler']):
        return 'Ev & Yaşam'

    # Tech check
    if cat == 'Teknoloji' or any(k in title_lower for k in ['kulaklık', 'hoparlör', 'powerbank', 'şarj', 'kablo', 'mouse', 'klavye', 'webcam', 'saat', 'pil', 'tıraş makinesi', 'wifi', 'modem', 'ssd', 'usb', 'hafıza kartı', 'koşu bandı']):
        return 'Teknoloji'

    return cat if cat in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam'] else 'Ev & Yaşam'

# Curate high quality pool
valid_pool = []
seen_titles = set()
for it in all_pools:
    title = it.get('title', '').strip()
    if not title or len(title) < 10:
        continue
    # Normalize title key to avoid near duplicates
    t_key = title[:35].lower()
    if t_key in seen_titles:
        continue

    orig = float(it.get('originalPrice', 0))
    disc = float(it.get('discountedPrice', 0))
    rate = int(it.get('discountRate', 0))
    if orig <= disc or disc <= 0 or rate < 15:
        continue

    purl = it.get('productUrl', '')
    iurl = it.get('imageUrl', '')
    if not purl.startswith('http') or not iurl.startswith('http'):
        continue

    store = it.get('store', '')
    if store not in ['Amazon TR', 'Hepsiburada', 'Idefix']:
        continue

    clean_cat = get_clean_cat(it)

    valid_pool.append({
        'title': title,
        'category': clean_cat,
        'store': store,
        'originalPrice': orig,
        'discountedPrice': disc,
        'discountRate': rate,
        'productUrl': purl,
        'imageUrl': iurl
    })
    seen_titles.add(t_key)

print(f"Total valid unique items: {len(valid_pool)}")
cats_dist = Counter(x['category'] for x in valid_pool)
print("By category:", dict(cats_dist))
stores_dist = Counter(x['store'] for x in valid_pool)
print("By store:", dict(stores_dist))

# Now build the new 120-item catalog:
# Target: 40 Amazon TR, 40 Hepsiburada, 40 Idefix
# Target: 30 Teknoloji, 30 Moda, 30 Kozmetik, 30 Ev & Yaşam
# Specifically, we want TOP TEKNOLOJİ items to be completely different from previous top items!
target_stores = ['Amazon TR', 'Hepsiburada', 'Idefix']
target_cats = ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']

# Group valid_pool by (category, store)
matrix = {}
for c in target_cats:
    for s in target_stores:
        matrix[(c, s)] = [x for x in valid_pool if x['category'] == c and x['store'] == s]
        # Sort by: not in previous top titles first, then by discountRate descending
        matrix[(c, s)].sort(key=lambda x: (x['title'].strip().lower() in current_titles, -x['discountRate']))

print("\nMatrix counts (Target is 10 for each (c, s)):")
for c in target_cats:
    row = [f"{s}: {len(matrix[(c, s)])}" for s in target_stores]
    print(f"  {c:11s} -> {', '.join(row)}")

# We need exactly 10 items for each of the 12 pairs! (10 * 3 stores = 30 per cat, 10 * 4 cats = 40 per store)
selected = []
for c in target_cats:
    for s in target_stores:
        available = matrix[(c, s)]
        # If less than 10, borrow from current catalog (properly clean)
        if len(available) < 10:
            existing = [x for x in current_catalog if x['category'] == c and x['store'] == s]
            for ex in existing:
                if len(available) >= 10:
                    break
                if ex['title'][:35].lower() not in set(y['title'][:35].lower() for y in available):
                    available.append(ex)
        
        # Pick 10
        picked = available[:10]
        selected.extend(picked)
        print(f"  Selected 10 for ({c}, {s})")

print(f"\nTotal selected: {len(selected)}")
print("Store counts:", dict(Counter(x['store'] for x in selected)))
print("Cat counts:", dict(Counter(x['category'] for x in selected)))

# Now put prominent, fresh products at the TOP of the new rotation:
# E.g. For Teknoloji:
# Rank 1: Logitech Webcam (%21, HB)
# Rank 2: Anker Soundcore Boom 2 (%53, HB)
# Rank 3: Xiaomi Powerbank (%38, Amazon)
# Rank 4: Spovan 4G Akıllı Saat (%16, Idefix)
# Rank 5: JBL Wave Beam Kulaklık (%40, HB)

# Interleave with zero consecutive collisions:
# (item[i].store != item[i+1].store AND item[i].category != item[i+1].category)
def solve_order(items_list):
    for attempt in range(2000):
        pool = list(items_list)
        random.shuffle(pool)

        # Let's find an exciting first item: a great new tech item
        first_idx = next((i for i, x in enumerate(pool) if x['category'] == 'Teknoloji' and any(k in x['title'].lower() for k in ['logitech', 'anker', 'xiaomi', 'spovan', 'jbl'])), 0)
        res = [pool.pop(first_idx)]

        success = True
        while pool:
            last = res[-1]
            candidates = [x for x in pool if x['store'] != last['store'] and x['category'] != last['category']]
            if not candidates:
                candidates = [x for x in pool if x['store'] != last['store']]
                if not candidates:
                    success = False
                    break
            
            rem_s = Counter(x['store'] for x in pool)
            rem_c = Counter(x['category'] for x in pool)
            candidates.sort(key=lambda x: rem_s[x['store']] + rem_c[x['category']], reverse=True)
            chosen = candidates[0]
            pool.remove(chosen)
            res.append(chosen)

        s_coll = sum(1 for i in range(len(res)-1) if res[i]['store'] == res[i+1]['store'])
        c_coll = sum(1 for i in range(len(res)-1) if res[i]['category'] == res[i+1]['category'])
        if s_coll == 0 and c_coll == 0:
            print(f"FOUND PERFECT ROTATION on attempt {attempt}!")
            return res
    return None

ordered_catalog = solve_order(selected)
if not ordered_catalog:
    print("Could not find perfect collision-free order in 2000 attempts!")
    sys.exit(1)

for i, it in enumerate(ordered_catalog):
    it['id'] = f"deal-{i+1:03d}"

# Print Top 5 of each category in the new catalog
print("\n" + "="*50)
print("=== YENİ DÖNGÜDEKİ TOP 5 ÜRÜNLER (KULLANICININ GÖRECEĞİ) ===")
print("="*50)
for cat in target_cats:
    cat_items = [x for x in ordered_catalog if x['category'] == cat]
    print(f"\n--- {cat} (Yeni İlk 5 Ürün) ---")
    for i, it in enumerate(cat_items[:5]):
        print(f"  {i+1}. [{it['store']:11s}] %{it['discountRate']:2d} | {it['title'][:65]}")

# 3. Save to local JSON files
with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(ordered_catalog, f, ensure_ascii=False, indent=2)

with open('scraper/final_equal_verified_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(ordered_catalog, f, ensure_ascii=False, indent=2)

compact_deals = []
for it in ordered_catalog:
    compact_deals.append({
        'id': it['id'],
        'title': it['title'],
        'category': it['category'],
        'store': it['store'],
        'originalPrice': it['originalPrice'],
        'discountedPrice': it['discountedPrice'],
        'discountRate': it['discountRate'],
        'productUrl': it['productUrl'],
        'imageUrl': it['imageUrl']
    })

with open('scraper/compact_deals.json', 'w', encoding='utf-8') as f:
    json.dump(compact_deals, f, ensure_ascii=False)

# 4. HTTP PUT to Primary REST API (ExtendsClass bin ccbacbe)
url = 'https://extendsclass.com/api/json-storage/bin/ccbacbe'
json_payload = json.dumps(compact_deals, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(url, data=json_payload, headers={'Content-Type': 'application/json'}, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print(f"\n[OK] ExtendsClass REST API güncellendi! HTTP {resp.status}")

# 5. Upload to Catbox Backup Mirror
res = subprocess.run(['curl.exe', '-s', '-F', 'reqtype=fileupload', '-F', 'fileToUpload=@scraper/compact_deals.json', 'https://catbox.moe/user/api.php'], capture_output=True, text=True)
catbox_url = res.stdout.strip()
print(f"[OK] Catbox Backup Mirror güncellendi: {catbox_url}")
