import requests
import urllib3
import json
from bs4 import BeautifulSoup

urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0'}

queries = ['kulaklik', 'kilif', 'kablo', 'sarj', 'termos', 'tencere', 'krem', 'parfum']

for q in queries:
    url = f"https://www.idefix.com/search?q={q}&sayfa=1"
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=6)
        if '__NEXT_DATA__' in r.text:
            soup = BeautifulSoup(r.text, 'html.parser')
            s = soup.find('script', id='__NEXT_DATA__')
            d = json.loads(s.string)
            items = d.get('props', {}).get('pageProps', {}).get('searchData', {}).get('items', [])
            total = d.get('props', {}).get('pageProps', {}).get('searchData', {}).get('totalCount')
            fifty_plus = 0
            for it in items:
                for v in it.get('variants', []):
                    p = float(v.get('price') or 0)
                    dp = float(v.get('discountedSalesPrice') or p)
                    if p > 0 and dp > 0 and dp < p:
                        rate = round(((p - dp) / p) * 100)
                        if rate >= 50:
                            fifty_plus += 1
            print(f"Query: {q:10} | Total: {total} | 50%+ in P1: {fifty_plus}")
    except Exception as e:
        print(f"Query {q} error: {e}")
