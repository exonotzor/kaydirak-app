import urllib.request
import json
import time
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

url = f"https://extendsclass.com/api/json-storage/bin/ccbacbe?t={int(time.time())}"
req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("Status:", resp.status)
    print("Total Deals on Live Server:", len(data))
    for cat in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
        items = [x for x in data if x['category'] == cat]
        print(f"\n--- Canlı Sunucu: {cat} (İlk 5 Ürün) ---")
        for i, it in enumerate(items[:5]):
            print(f"  {i+1}. [{it['store']:11s}] %{it['discountRate']:2d} | {it['title']}")
