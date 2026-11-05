import requests
import urllib3
import json
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get('https://www.idefix.com/kampanyalar/elektronik-80', headers=headers, verify=False, timeout=8)
soup = BeautifulSoup(r.text, 'html.parser')
s = soup.find('script', id='__NEXT_DATA__')
if s and s.string:
    d = json.loads(s.string)
    pp = d.get('props', {}).get('pageProps', {})
    widgets = pp.get('widgets', [])
    print(f"Total widgets: {len(widgets)}")
    for w in widgets:
        print('Widget title:', w.get('title'), 'type:', w.get('type'), 'componentType:', w.get('componentType'))
        for p in w.get('products', [])[:3]:
            v0 = p.get('variants', [{}])[0]
            print(f"  Product: {p.get('name')[:35]} | Price: {v0.get('price')} -> {v0.get('discountedSalesPrice')}")
