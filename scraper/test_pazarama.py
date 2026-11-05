import requests
import urllib3
import json
import re

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

r = requests.get('https://www.pazarama.com/bilgisayar-ve-tablet-c-200000000', headers=headers, verify=False, timeout=8)
print('Pazarama status:', r.status_code)
match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text)
if match:
    d = json.loads(match.group(1))
    pp = d.get('props', {}).get('pageProps', {})
    print('Pazarama Next data keys:', list(pp.keys()))
    # search for products
    for k, v in pp.items():
        if isinstance(v, dict):
            print(f"Key {k} dict: {list(v.keys())[:5]}")
        elif isinstance(v, list):
            print(f"Key {k} list len: {len(v)}")
