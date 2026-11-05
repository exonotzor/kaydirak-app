import urllib.request
import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

url = "https://extendsclass.com/api/json-storage/bin/faddbde"
req = urllib.request.Request(url, headers={"User-Agent": "Flutter/DealService"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print("Response Type:", type(data))
    print("Total Deals:", len(data))
    tech = [x for x in data if x.get("category") == "Teknoloji"]
    print("Teknoloji Toplam:", len(tech))
    print("\nTop 5 Teknoloji Ürünü:")
    for i, x in enumerate(tech[:5]):
        print(f"  {i+1}. {x.get('title')} ({x.get('store')}) %{x.get('discountRate')}")
