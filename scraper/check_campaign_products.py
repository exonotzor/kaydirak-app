import requests
import urllib3
import json
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0'}

campaign_urls = [
    ('Teknoloji', 'https://www.idefix.com/kampanyalar/elektronik-80'),
    ('Teknoloji', 'https://www.idefix.com/kampanyalar/gamerfix-62'),
    ('Ev & Yaşam', 'https://www.idefix.com/kampanyalar/ev-yasam-46'),
    ('Kozmetik', 'https://www.idefix.com/kampanyalar/kozmetik-kisisel-bakim-31'),
    ('Kozmetik', 'https://www.idefix.com/kampanyalar/bakim-gunleri-163'),
]

for cat, url in campaign_urls:
    r = requests.get(url, headers=headers, verify=False, timeout=8)
    soup = BeautifulSoup(r.text, 'html.parser')
    s = soup.find('script', id='__NEXT_DATA__')
    if s and s.string:
        d = json.loads(s.string)
        pp = d.get('props', {}).get('pageProps', {})
        # look for campaign components or products
        print(f"\n--- {cat}: {url} ---")
        print('pageProps keys:', list(pp.keys()))
        def find_products(obj, path=""):
            if isinstance(obj, dict):
                if 'variants' in obj and 'name' in obj:
                    v = obj['variants'][0] if obj['variants'] else {}
                    p = float(v.get('price') or 0)
                    dp = float(v.get('discountedSalesPrice') or p)
                    if p > 0 and dp > 0 and dp < p:
                        rate = round(((p - dp) / p) * 100)
                        if rate >= 50:
                            print(f"  Found 50%+ deal: {rate}% | {dp} TL (was {p} TL) | {obj.get('name')[:40]}")
                for k, val in obj.items():
                    find_products(val, f"{path}.{k}")
            elif isinstance(obj, list):
                for item in obj[:20]:
                    find_products(item, path)
        find_products(pp)
