import requests
import urllib3
import json
from bs4 import BeautifulSoup

urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0'}

for p in [1, 2, 3]:
    r = requests.get(f'https://yaniyo.com/elektronik?rate=50&page={p}', headers=headers, verify=False, timeout=8)
    soup = BeautifulSoup(r.text, 'html.parser')
    s = soup.find('script', id='__NEXT_DATA__')
    if s:
        d = json.loads(s.string)
        prods = d['props']['pageProps']['initialProducts']
        print(f"Page {p}: {len(prods)} products")
        if prods:
            print(f"  First: {prods[0]['name'][:40]} | {prods[0]['currentPrice']} TL | -%{round(prods[0]['currentDiscount'])}")
