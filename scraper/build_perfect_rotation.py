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

# 1. Load the pristine verified catalog
with open('scraper/final_equal_verified_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"Base catalog length: {len(catalog)}")

# Clean any non-tech out of Teknoloji
non_tech_words = [
    'krem', 'serum', 'losyon', 'nemlendirici', 'hydro boost', 'nivea', 'neutrogena',
    'loreal', 'parfüm', 'parfum', 'deodorant', 'şampuan', 'sampuan', 'maske', 'makyaj',
    'ruj', 'rimel', 'maskara', 'cilt', 'bakım yağı', 'tonik', 'güneş kremi', 'skinmaster',
    'yelek', 'mont', 'şort', 'sort', 'kapri', 'pantolon', 't-shirt', 'tişört', 'kazak',
    'hırka', 'sweatshirt', 'swetşört', 'ayakkabı', 'bot', 'çorap', 'ceket', 'gömlek',
    'polar', 'tayt', 'içlik', 'boxer', 'kaban', 'atlet', 'elbise', 'etek', 'buzluk',
    'cooler', 'stein', 'bardak', 'termos', 'matara', 'tava', 'tencere'
]

# Separate by category
tech_items = [x for x in catalog if x['category'] == 'Teknoloji' and not any(w in x['title'].lower() for w in non_tech_words)]
moda_items = [x for x in catalog if x['category'] == 'Moda']
kozmetik_items = [x for x in catalog if x['category'] == 'Kozmetik']
ev_items = [x for x in catalog if x['category'] == 'Ev & Yaşam']

print(f"Tech items (pure): {len(tech_items)}")
print(f"Moda items: {len(moda_items)}")
print(f"Kozmetik items: {len(kozmetik_items)}")
print(f"Ev & Yaşam items: {len(ev_items)}")

# If tech_items < 30, add pure tech items
if len(tech_items) < 30:
    # load tech pool
    with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
        pool = json.load(f)
    for p in pool:
        if len(tech_items) >= 30:
            break
        t = p['title'].lower()
        if any(k in t for k in ['kulaklık', 'hoparlör', 'powerbank', 'şarj', 'kablo', 'mouse', 'klavye', 'webcam', 'akıllı saat', 'kol saati', 'tıraş makinesi']):
            if not any(w in t for w in non_tech_words):
                if p['title'][:35].lower() not in set(x['title'][:35].lower() for x in tech_items):
                    tech_items.append({
                        'title': p['title'],
                        'category': 'Teknoloji',
                        'store': p['store'],
                        'originalPrice': float(p['originalPrice']),
                        'discountedPrice': float(p['discountedPrice']),
                        'discountRate': int(p['discountRate']),
                        'productUrl': p['productUrl'],
                        'imageUrl': p['imageUrl']
                    })

# Balance stores inside each category to exactly 10 Amazon, 10 HB, 10 Idefix
def balance_category(cat_name, items):
    by_s = {'Amazon TR': [], 'Hepsiburada': [], 'Idefix': []}
    for it in items:
        it['category'] = cat_name
        by_s[it['store']].append(it)
    
    print(f"  {cat_name} raw stores: Amazon {len(by_s['Amazon TR'])}, HB {len(by_s['Hepsiburada'])}, Idefix {len(by_s['Idefix'])}")
    
    # We will pick 10 from each store
    balanced = []
    for s in ['Amazon TR', 'Hepsiburada', 'Idefix']:
        balanced.extend(by_s[s][:10])
    return balanced

# Check current catalog items and balance
# Since catalog originally has 40 Amazon, 40 HB, 40 Idefix (10 of each store per category):
cat_groups = {
    'Teknoloji': [x for x in catalog if x['category'] == 'Teknoloji'],
    'Moda': [x for x in catalog if x['category'] == 'Moda'],
    'Kozmetik': [x for x in catalog if x['category'] == 'Kozmetik'],
    'Ev & Yaşam': [x for x in catalog if x['category'] == 'Ev & Yaşam']
}

# Verify no non-tech in Teknoloji
for i, x in enumerate(cat_groups['Teknoloji']):
    if any(w in x['title'].lower() for w in non_tech_words):
        print(f"Removing polluted tech item: {x['title']}")
        # replace with pure tech item of same store
        if x['store'] == 'Idefix':
            cat_groups['Teknoloji'][i] = {
                'title': 'Spovan Vision 4G SIM Kart Kameralı Sesli Görüşme GPS Akıllı Saat',
                'category': 'Teknoloji',
                'store': 'Idefix',
                'originalPrice': 2499.0,
                'discountedPrice': 2099.0,
                'discountRate': 16,
                'productUrl': 'https://www.idefix.com//spovan-vision-4g-sim-kart-kamerali-sesli-gorusme-gps-akilli-saat-p-15632147',
                'imageUrl': 'https://image01.idefix.com/resize/600/600/product/15632147/spovan-vision-4g-691672323a6c7.jpg'
            }
        elif x['store'] == 'Amazon TR':
            cat_groups['Teknoloji'][i] = {
                'title': '10.000 mAh Manyetik Kablosuz Powerbank 15W, 22.5W Type-C Hızlı Şarj Cihazı',
                'category': 'Teknoloji',
                'store': 'Amazon TR',
                'originalPrice': 2999.0,
                'discountedPrice': 1990.0,
                'discountRate': 34,
                'productUrl': 'https://www.amazon.com.tr/dp/B0HLFPLDPQ',
                'imageUrl': 'https://m.media-amazon.com/images/I/71aj9YoJy8L._AC_UL320_.jpg'
            }
        else:
            cat_groups['Teknoloji'][i] = {
                'title': 'Xiaomi Redmi Buds 6 Play - Siyah Kulakiçi Kulaklık TWS (Xiaomi Türkiye Garantili)',
                'category': 'Teknoloji',
                'store': 'Hepsiburada',
                'originalPrice': 1190.0,
                'discountedPrice': 797.2,
                'discountRate': 33,
                'productUrl': 'https://www.hepsiburada.com/redmi-buds-6-play-siyah-kulakici-kulaklik-tws-xiaomi-turkiye-garantili-p-HBCV000072PXK3',
                'imageUrl': 'https://productimages.hepsiburada.net/s/777/300-400/110000792817673.jpg'
            }

# ROTATION LOGIC:
# For every category, shift items by 10 positions so the previous top items are moved to the end,
# and brand new items appear at ranks 1, 2, 3, 4, 5!
rotated_all = []
for c, items in cat_groups.items():
    # Rotate by 10
    rotated_items = items[10:] + items[:10]
    cat_groups[c] = rotated_items
    print(f"{c} rotated: New #1 is '{rotated_items[0]['title'][:50]}' ({rotated_items[0]['store']})")
    rotated_all.extend(rotated_items)

# Make sure Teknoloji #1 is exciting:
# Let's put Xiaomi Redmi Buds 6 Play (%33) or Anker Boom 2 (%53) at #1 of Teknoloji!
tech_hb = [x for x in cat_groups['Teknoloji'] if 'xiaomi redmi buds 6' in x['title'].lower() or 'anker' in x['title'].lower()]
if tech_hb:
    cat_groups['Teknoloji'].remove(tech_hb[0])
    cat_groups['Teknoloji'].insert(0, tech_hb[0])

# Interleave cleanly so no adjacent store collisions AND no adjacent category collisions
all_120 = []
for c in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
    all_120.extend(cat_groups[c])

print(f"\nTotal items to interleave: {len(all_120)}")
print("Store counts:", dict(Counter(x['store'] for x in all_120)))
print("Cat counts:", dict(Counter(x['category'] for x in all_120)))

def solve_order(pool_items):
    for attempt in range(3000):
        pool = list(pool_items)
        random.shuffle(pool)

        # Place the new Teknoloji #1 item first!
        new_top_tech = next(x for x in pool if x['category'] == 'Teknoloji' and ('xiaomi redmi buds' in x['title'].lower() or 'anker' in x['title'].lower()))
        pool.remove(new_top_tech)
        res = [new_top_tech]

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
            print(f"FOUND ZERO-COLLISION ROTATION on attempt {attempt}!")
            return res
    return None

final_order = solve_order(all_120)
if not final_order:
    print("Could not find order, exiting!")
    sys.exit(1)

for i, it in enumerate(final_order):
    it['id'] = f"deal-{i+1:03d}"

# Check results
print("\n" + "="*60)
print("=== 4 SAAT SONRAKİ YENİ İNDİRİM KATALOĞU (YENİ TOP ÜRÜNLER) ===")
print("="*60)
for cat in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
    items = [x for x in final_order if x['category'] == cat]
    print(f"\n--- {cat} (Yeni İlk 5 Ürün) ---")
    for i, it in enumerate(items[:5]):
        print(f"  {i+1}. [{it['store']:11s}] %{it['discountRate']:2d} | {it['title'][:65]}")

# Save to local files
with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(final_order, f, ensure_ascii=False, indent=2)

with open('scraper/final_equal_verified_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(final_order, f, ensure_ascii=False, indent=2)

compact_deals = []
for it in final_order:
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

# Send HTTP PUT to Primary REST API (ExtendsClass bin ccbacbe)
url = 'https://extendsclass.com/api/json-storage/bin/ccbacbe'
json_payload = json.dumps(compact_deals, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(url, data=json_payload, headers={'Content-Type': 'application/json'}, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print(f"\n[OK] ExtendsClass REST API güncellendi! HTTP {resp.status}")

# Upload to Catbox
res = subprocess.run(['curl.exe', '-s', '-F', 'reqtype=fileupload', '-F', 'fileToUpload=@scraper/compact_deals.json', 'https://catbox.moe/user/api.php'], capture_output=True, text=True)
catbox_url = res.stdout.strip()
print(f"[OK] Catbox Backup Mirror güncellendi: {catbox_url}")
