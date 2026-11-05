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

# Load existing clean catalog
with open('scraper/final_equal_verified_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# Group by (category, store)
by_cat_store = {}
for it in catalog:
    c = it['category']
    s = it['store']
    by_cat_store.setdefault((c, s), []).append(it)

# Extra HB cosmetics if needed to reach exactly 10
extra_hb_cosmetics = [
    {
        "title": "L'Oreal Paris Revitalift Lazer Saf Retinol Gece Serumu 30 ml",
        "category": "Kozmetik",
        "store": "Hepsiburada",
        "originalPrice": 899.9,
        "discountedPrice": 499.0,
        "discountRate": 45,
        "productUrl": "https://www.hepsiburada.com/l-oreal-paris-revitalift-lazer-saf-retinol-gece-serumu-30-ml-p-HBCV000007R6X4",
        "imageUrl": "https://productimages.hepsiburada.net/s/54/375-375/11186780078130.jpg"
    },
    {
        "title": "Maybelline New York Lash Sensational Sky High Maskara Siyah",
        "category": "Kozmetik",
        "store": "Hepsiburada",
        "originalPrice": 629.9,
        "discountedPrice": 379.0,
        "discountRate": 40,
        "productUrl": "https://www.hepsiburada.com/maybelline-new-york-lash-sensational-sky-high-maskara-siyah-p-HBCV0000030O67",
        "imageUrl": "https://productimages.hepsiburada.net/s/49/375-375/110000010041444.jpg"
    },
    {
        "title": "Garnier Saf & Temiz Kömürlü 3'ü 1 Arada Yüz Temizleme Jeli 150 ml",
        "category": "Kozmetik",
        "store": "Hepsiburada",
        "originalPrice": 299.9,
        "discountedPrice": 179.9,
        "discountRate": 40,
        "productUrl": "https://www.hepsiburada.com/garnier-saf-ve-temiz-komurlu-3-u-1-arada-150-ml-p-SGKLE000003444",
        "imageUrl": "https://productimages.hepsiburada.net/s/21/375-375/9924976410674.jpg"
    },
    {
        "title": "Bioderma Sensibio H2O Micellar Cilt Temizleme Suyu 500 ml",
        "category": "Kozmetik",
        "store": "Hepsiburada",
        "originalPrice": 750.0,
        "discountedPrice": 487.5,
        "discountRate": 35,
        "productUrl": "https://www.hepsiburada.com/bioderma-sensibio-h2o-500-ml-p-HBV00000E325Q",
        "imageUrl": "https://productimages.hepsiburada.net/s/32/375-375/10360700469298.jpg"
    }
]

for it in extra_hb_cosmetics:
    by_cat_store.setdefault(('Kozmetik', 'Hepsiburada'), []).append(it)

# Ensure each of the 12 pairs has EXACTLY 10 items
categories = ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']
stores = ['Amazon TR', 'Hepsiburada', 'Idefix']

# Specific Rotation: Define the desired top products for each category
top_tech = [
    {
        "title": "Anker Soundcore Boom 2 Bluetooth 5.3 Hoparlör, 80W, IPX7 Su Geçirmez",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "originalPrice": 13300.0,
        "discountedPrice": 6299.0,
        "discountRate": 53,
        "productUrl": "https://www.hepsiburada.com/anker-soundcore-boom-2-bluetooth-5-3-hoparlor-80w-ipx7-su-gecirmez-yesil-a3138-p-HBCV00006ODGJ5",
        "imageUrl": "https://productimages.hepsiburada.net/s/777/375-375/110000731638248.jpg"
    },
    {
        "title": "10.000 mAh Manyetik Kablosuz Powerbank 15W, 22.5W Type-C Hızlı Şarj Cihazı",
        "category": "Teknoloji",
        "store": "Amazon TR",
        "originalPrice": 2999.0,
        "discountedPrice": 1990.0,
        "discountRate": 34,
        "productUrl": "https://www.amazon.com.tr/dp/B0HLFPLDPQ",
        "imageUrl": "https://m.media-amazon.com/images/I/71aj9YoJy8L._AC_UL320_.jpg"
    },
    {
        "title": "Spovan Vision 4G SIM Kart Kameralı Sesli Görüşme GPS Akıllı Saat",
        "category": "Teknoloji",
        "store": "Idefix",
        "originalPrice": 2499.0,
        "discountedPrice": 2099.0,
        "discountRate": 16,
        "productUrl": "https://www.idefix.com//spovan-vision-4g-sim-kart-kamerali-sesli-gorusme-gps-akilli-saat-p-15632147",
        "imageUrl": "https://image01.idefix.com/resize/600/600/product/15632147/spovan-vision-4g-691672323a6c7.jpg"
    },
    {
        "title": "Logitech BRIO 100 Full HD 1080p Gizlilik Kapaklı Mikrofonlu Webcam",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "originalPrice": 1599.0,
        "discountedPrice": 1269.0,
        "discountRate": 21,
        "productUrl": "https://www.hepsiburada.com/logitech-brio-100-full-hd-1080p-gizlilik-kapakli-mikrofonlu-webcam-grafit-p-HBCV000057J3GQ",
        "imageUrl": "https://productimages.hepsiburada.net/s/475/375-375/110000518388656.jpg"
    },
    {
        "title": "Xiaomi Redmi Buds 6 Play - Siyah Kulakiçi Kulaklık TWS (Xiaomi Türkiye Garantili)",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "originalPrice": 1190.0,
        "discountedPrice": 797.2,
        "discountRate": 33,
        "productUrl": "https://www.hepsiburada.com/redmi-buds-6-play-siyah-kulakici-kulaklik-tws-xiaomi-turkiye-garantili-p-HBCV000072PXK3",
        "imageUrl": "https://productimages.hepsiburada.net/s/777/300-400/110000792817673.jpg"
    }
]

# Pick exactly 10 for each pair
curated_120 = []
for c in categories:
    for s in stores:
        pool = by_cat_store.get((c, s), [])
        # deduplicate
        seen = set()
        clean_p = []
        for x in pool:
            k = x['title'][:35].lower()
            if k not in seen:
                clean_p.append(x)
                seen.add(k)
        
        # If c == 'Teknoloji', prioritize top_tech
        if c == 'Teknoloji':
            store_top = [x for x in top_tech if x['store'] == s]
            clean_p = store_top + [x for x in clean_p if x['title'][:35].lower() not in set(y['title'][:35].lower() for y in store_top)]

        # Take exactly 10
        pair_10 = clean_p[:10]
        curated_120.extend(pair_10)
        print(f"Pair ({c}, {s}) -> {len(pair_10)} items")

print(f"\nTotal curated: {len(curated_120)}")
print("Store distribution:", dict(Counter(x['store'] for x in curated_120)))
print("Category distribution:", dict(Counter(x['category'] for x in curated_120)))

# Interleave with zero collisions
def solve_order(pool_items):
    for attempt in range(4000):
        pool = list(pool_items)
        random.shuffle(pool)

        # Place Anker Boom 2 first as the big spotlight deal!
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
            print(f"FOUND ZERO-COLLISION ROTATION on attempt {attempt}!")
            return res
    return None

final_deals = solve_order(curated_120)
if not final_deals:
    print("Failed to find zero collision arrangement!")
    sys.exit(1)

for i, it in enumerate(final_deals):
    it['id'] = f"deal-{i+1:03d}"

# Print Top 5 of each category
print("\n" + "="*60)
print("=== 4 SAAT SONRAKİ ROTASYON KATALOĞU (MOBİLDE GÖRÜNECEKLER) ===")
print("="*60)
for cat in categories:
    items = [x for x in final_deals if x['category'] == cat]
    print(f"\n--- {cat} (Yeni İlk 5 Ürün) ---")
    for i, it in enumerate(items[:5]):
        print(f"  {i+1}. [{it['store']:11s}] %{it['discountRate']:2d} | {it['title'][:65]}")

# Save to local files
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
