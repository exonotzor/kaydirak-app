import requests
import urllib3
import json
import re

urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://www.idefix.com/cep-telefonu-aksesuarlari-c-2313374140'
r = requests.get(url, headers=headers, verify=False)
print("status:", r.status_code)
m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text)
if m:
    d = json.loads(m.group(1))
    items = d.get('props', {}).get('pageProps', {}).get('categoryData', {}).get('items', [])
    print("items in cep telefonu aksesuarları:", len(items))
    for it in items[:5]:
        v0 = it.get('variants', [])[0]
        p = v0.get('price')
        dp = v0.get('discountedSalesPrice')
        print(f"Name: {v0.get('name')[:40]} | Price: {p} | Discounted: {dp}")
