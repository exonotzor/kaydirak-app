import requests
import urllib3
from bs4 import BeautifulSoup
import re
import json

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = 'https://www.idefix.com/us-polo-assn-kadin-beyaz-uzun-kollu-basic-gomlek-50324791-vr013-p-26711236'
r = requests.get(url, headers=headers, verify=False, timeout=10)
print('Idefix status:', r.status_code)

# Search for any json ld in script type="application/ld+json"
soup = BeautifulSoup(r.text, 'html.parser')
for s in soup.find_all('script', type='application/ld+json'):
    try:
        data = json.loads(s.string)
        print('LD+JSON type:', data.get('@type'))
        if data.get('@type') == 'Product':
            print('Product name:', data.get('name'))
            offers = data.get('offers', {})
            print('Offers:', offers.get('price'), offers.get('priceCurrency'))
    except Exception:
        pass

# Also look for Next.js data
s = soup.find('script', id='__NEXT_DATA__')
if s and s.string:
    d = json.loads(s.string)
    pp = d.get('props', {}).get('pageProps', {})
    print('pageProps keys:', list(pp.keys()))
    # dump all prices or product info
    def search_keys(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ['price', 'discountedSalesPrice', 'originalPrice', 'salesPrice', 'name', 'title']:
                    print(f"Found {path}.{k} = {v}")
                search_keys(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj[:3]):
                search_keys(v, f"{path}[{i}]")
    search_keys(pp, "pp")
