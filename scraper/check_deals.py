import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

print(f"Total deals: {len(deals)}")
for d in deals:
    if d['store'] in ['Amazon TR', 'Hepsiburada']:
        print("---")
        print(f"Store: {d['store']}")
        print(f"Title: {d['title']}")
        print(f"Price: {d['discountedPrice']} TL (Orig: {d['originalPrice']} TL, Disc: %{d['discountRate']})")
        print(f"URL: {d['productUrl']}")
        print(f"Image: {d['imageUrl']}")
        # Test URL status
        try:
            r = requests.head(d['productUrl'], headers=headers, verify=False, timeout=5, allow_redirects=True)
            print(f"URL HTTP status: {r.status_code}")
        except Exception as e:
            print(f"URL fetch error: {e}")
