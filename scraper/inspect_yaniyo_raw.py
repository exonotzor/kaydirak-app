import requests
import urllib3
import json
import re

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

r = requests.get('https://yaniyo.com/elektronik', headers=headers, verify=False, timeout=10)
match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text)
if match:
    d = json.loads(match.group(1))
    prods = d.get('props', {}).get('pageProps', {}).get('initialProducts', [])
    print('Total prods:', len(prods))
    for p in prods[:5]:
        print('Name:', p.get('name'))
        print('curPrice:', p.get('currentPrice'))
        print('curDisc:', p.get('currentDiscount'))
        print('priceList:', p.get('priceList'))
        print('shortId:', p.get('shortId'))
        print('---')
