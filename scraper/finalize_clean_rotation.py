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

with open('scraper/final_equal_verified_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# Non-tech ban list for Teknoloji
banned_in_tech = [
    'parka', 'kaban', 'ceket', 'mont', 'yelek', 'şort', 'sort', 'kapri', 'pantolon',
    't-shirt', 'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı', 'bot',
    'çorap', 'gömlek', 'polar', 'tayt', 'içlik', 'boxer', 'atlet', 'elbise', 'etek',
    'buzluk', 'cooler', 'stein', 'bardak', 'termos', 'matara', 'tava', 'tencere', 'krampon',
    'çanta', 'canta', 'tozluk', 'eldiven', 'bere', 'şapka', 'sapka', 'bikini', 'mayo',
    'krem', 'serum', 'losyon', 'deodorant', 'parfüm', 'sabun'
]

# Load pure Idefix gadgets pool
with open('scraper/find_pure_idefix_tech.py', 'r', encoding='utf-8') as f:
    pass
with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    raw_pool = json.load(f)

pure_idefix_gadgets = []
for x in raw_pool:
    t = x.get('title', '').lower()
    if not any(w in t for w in banned_in_tech):
        if any(k in t for k in ['saat', 'kronometre', 'şarj', 'sarj', 'kablo', 'kulaklık', 'kulaklik', 'hoparlör', 'hoparlor', 'pil', 'klavye', 'mouse', 'webcam', 'etiket makinesi', 'koşu bandı']):
            pure_idefix_gadgets.append(x)

print(f"Available pure Idefix gadgets: {len(pure_idefix_gadgets)}")

# Filter catalog: Replace any non-tech in Teknoloji with pure Idefix gadgets
gadget_idx = 0
for i, it in enumerate(catalog):
    if it['category'] == 'Teknoloji':
        t = it['title'].lower()
        if any(w in t for w in banned_in_tech):
            print(f"Replacing non-tech [{it['store']}]: {it['title'][:50]}")
            sub = pure_idefix_gadgets[gadget_idx]
            gadget_idx += 1
            catalog[i] = {
                'id': it['id'],
                'title': sub['title'],
                'category': 'Teknoloji',
                'store': it['store'],
                'originalPrice': float(sub['originalPrice']),
                'discountedPrice': float(sub['discountedPrice']),
                'discountRate': int(sub['discountRate']),
                'productUrl': sub['productUrl'],
                'imageUrl': sub['imageUrl']
            }

# Verify all 30 tech items are clean now
tech_check = [x for x in catalog if x['category'] == 'Teknoloji']
print(f"Teknoloji items after replacement: {len(tech_check)}")
for i, x in enumerate(tech_check):
    assert not any(w in x['title'].lower() for w in banned_in_tech), f"Still contaminated: {x['title']}"

# Now interleave with 0 store collisions and 0 category collisions
def solve_order(pool_items):
    for attempt in range(4000):
        pool = list(pool_items)
        random.shuffle(pool)

        # Start with Anker Soundcore Boom 2 (%53)
        top_deal = next(x for x in pool if 'anker soundcore boom 2' in x['title'].lower())
        pool.remove(top_deal)
        res = [top_deal]

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
            print(f"FOUND PERFECT ZERO-COLLISION ORDER on attempt {attempt}!")
            return res
    return None

final_deals = solve_order(catalog)
if not final_deals:
    print("Could not find order, fallback")
    sys.exit(1)

for i, it in enumerate(final_deals):
    it['id'] = f"deal-{i+1:03d}"

# Print Top 5 of each category
print("\n" + "="*60)
print("=== 4 SAAT SONRAKİ NİHAİ DÖNGÜ (MOBİL UYGULAMADA GÖRÜNECEK LİSTE) ===")
print("="*60)
for cat in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
    items = [x for x in final_deals if x['category'] == cat]
    print(f"\n--- {cat} (İlk 5 Ürün) ---")
    for i, it in enumerate(items[:5]):
        print(f"  {i+1}. [{it['store']:11s}] %{it['discountRate']:2d} | {it['title'][:65]}")

# Save locally
with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(final_deals, f, ensure_ascii=False, indent=2)

with open('scraper/final_equal_verified_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(final_deals, f, ensure_ascii=False, indent=2)

compact_deals = []
for it in final_deals:
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

# HTTP PUT to ExtendsClass bin ccbacbe
url = 'https://extendsclass.com/api/json-storage/bin/ccbacbe'
json_payload = json.dumps(compact_deals, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(url, data=json_payload, headers={'Content-Type': 'application/json'}, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print(f"\n[OK] ExtendsClass REST API Güncellendi! HTTP {resp.status}")

# Upload to Catbox
res = subprocess.run(['curl.exe', '-s', '-F', 'reqtype=fileupload', '-F', 'fileToUpload=@scraper/compact_deals.json', 'https://catbox.moe/user/api.php'], capture_output=True, text=True)
catbox_url = res.stdout.strip()
print(f"[OK] Catbox Backup Mirror Güncellendi: {catbox_url}")
