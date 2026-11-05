import requests
import urllib3
import json
import re

urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

url = 'https://www.idefix.com/kulakliklar-c-2313670940'
r = requests.get(url, headers=headers, verify=False, timeout=10)
match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text)
if match:
    d = json.loads(match.group(1))
    pp = d.get('props', {}).get('pageProps', {})
    print('pageProps keys:', list(pp.keys()))
    cd = pp.get('categoryData', {})
    if isinstance(cd, dict):
        print('categoryData keys:', list(cd.keys()))
        items = cd.get('items', [])
        print('items count:', len(items))
        if items:
            print('first item name:', items[0].get('name'))
            print('first item variants:', len(items[0].get('variants', [])))
            v0 = items[0].get('variants', [])[0]
            print('variant 0:', v0.get('price'), v0.get('discountedSalesPrice'))
