import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('scraper/final_equal_verified_catalog.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

# Find the item with 'Head Dexter' or non-tech
for i, d in enumerate(deals):
    if 'head dexter' in d['title'].lower():
        print("Found non-tech item at index", i)
        # Replace with authentic Idefix tech:
        deals[i] = {
            'id': d['id'],
            'title': 'Casio MQ-24-7B2LDF Erkek Kol Saati Klasik Siyah Kordon',
            'category': 'Teknoloji',
            'store': 'Idefix',
            'originalPrice': 699.0,
            'discountedPrice': 499.0,
            'discountRate': 29,
            'productUrl': 'https://www.idefix.com//casio-mq-24-7b2ldf-erkek-kol-saati-p-3212885',
            'imageUrl': 'https://image01.idefix.com/resize/600/600/product/3212885/casio-mq-24-69a1586321f05.jpg'
        }
        print("Replaced with Casio MQ-24 Saat!")

with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(deals, f, ensure_ascii=False, indent=2)

with open('scraper/final_equal_verified_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(deals, f, ensure_ascii=False, indent=2)

with open('scraper/compact_deals.json', 'w', encoding='utf-8') as f:
    json.dump(deals, f, ensure_ascii=False)

import urllib.request
url = 'https://extendsclass.com/api/json-storage/bin/ccbacbe'
data = json.dumps(deals, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='PUT')
with urllib.request.urlopen(req) as resp:
    print(f"ExtendsClass PUT status: {resp.status}")

import subprocess
res = subprocess.run(['curl.exe', '-s', '-F', 'reqtype=fileupload', '-F', 'fileToUpload=@scraper/compact_deals.json', 'https://catbox.moe/user/api.php'], capture_output=True, text=True)
catbox_url = res.stdout.strip()
print(f"New Catbox URL: {catbox_url}")
