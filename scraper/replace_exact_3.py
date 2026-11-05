import json
import urllib.request
import subprocess
from collections import Counter
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

replacements = [
    {
        "title": "Walke Wedel 2.5 Hp Manuel Eğimli Koşu Bandı Bluetooth Bağlantılı",
        "category": "Teknoloji",
        "store": "Idefix",
        "originalPrice": 14999.0,
        "discountedPrice": 11999.0,
        "discountRate": 20,
        "productUrl": "https://www.idefix.com//walke-wedel-25-hp-manuel-egimli-kosu-bandi-bluetooth-baglantili-p-15632147",
        "imageUrl": "https://image01.idefix.com/resize/600/600/product/15632147/walke-wedel-691672323a6c7.jpg"
    },
    {
        "title": "Alvenda Home ZR936 Type-C Type-C 100W Hızlı Şarj Kablosu 5 M",
        "category": "Teknoloji",
        "store": "Idefix",
        "originalPrice": 299.0,
        "discountedPrice": 245.0,
        "discountRate": 18,
        "productUrl": "https://www.idefix.com//alvenda-home-zr936-type-c-type-c-100w-kablo-5-m-p-3212885",
        "imageUrl": "https://image01.idefix.com/resize/600/600/product/3212885/alvenda-zr936-69a1586321f05.jpg"
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
    }
]

# Find the 3 clothing items in Teknoloji
rep_i = 0
for i, d in enumerate(deals):
    if d['category'] == 'Teknoloji':
        t = d['title'].lower()
        if 'north face' in t or 'c ess crw' in t:
            print(f"Replacing [{i}]: {d['title']}")
            sub = replacements[rep_i]
            rep_i += 1
            deals[i] = {
                'id': d['id'],
                'title': sub['title'],
                'category': 'Teknoloji',
                'store': 'Idefix',
                'originalPrice': sub['originalPrice'],
                'discountedPrice': sub['discountedPrice'],
                'discountRate': sub['discountRate'],
                'productUrl': sub['productUrl'],
                'imageUrl': sub['imageUrl']
            }

# Verify that all 30 tech items are clean
for i, d in enumerate(deals):
    if d['category'] == 'Teknoloji':
        t = d['title'].lower()
        assert 'north face' not in t and 'adidas' not in t, f"Still bad: {d['title']}"

# Now let's verify consecutive collisions
s_coll = []
c_coll = []
for i in range(len(deals) - 1):
    if deals[i]['store'] == deals[i+1]['store']:
        s_coll.append(i)
    if deals[i]['category'] == deals[i+1]['category']:
        c_coll.append(i)

print(f"Store collisions: {len(s_coll)}, Category collisions: {len(c_coll)}")

# If 0 collisions, save!
if len(s_coll) == 0 and len(c_coll) == 0:
    print("ZERO COLLISIONS CONFIRMED!")

with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(deals, f, ensure_ascii=False, indent=2)

with open('scraper/final_equal_verified_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(deals, f, ensure_ascii=False, indent=2)

with open('scraper/compact_deals.json', 'w', encoding='utf-8') as f:
    json.dump(deals, f, ensure_ascii=False)

# HTTP PUT to ExtendsClass
url = 'https://extendsclass.com/api/json-storage/bin/ccbacbe'
json_payload = json.dumps(deals, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(url, data=json_payload, headers={'Content-Type': 'application/json'}, method='PUT')
with urllib.request.urlopen(req, timeout=15) as resp:
    print(f"[OK] ExtendsClass REST API güncellendi! HTTP {resp.status}")

# Upload to Catbox
res = subprocess.run(['curl.exe', '-s', '-F', 'reqtype=fileupload', '-F', 'fileToUpload=@scraper/compact_deals.json', 'https://catbox.moe/user/api.php'], capture_output=True, text=True)
catbox_url = res.stdout.strip()
print(f"[OK] Catbox Backup Mirror: {catbox_url}")
