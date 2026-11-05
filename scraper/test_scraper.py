import requests
import urllib3
import json
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

url = 'https://www.idefix.com/grup-alisverisi-firsatlari-gl-130661'
r = requests.get(url, headers=headers, verify=False, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')
if script and script.string:
    data = json.loads(script.string)
    ld = data.get('props', {}).get('pageProps', {}).get('landingData', {})
    print("landingData keys:", list(ld.keys()) if isinstance(ld, dict) else len(ld))
    items = ld.get('items', [])
    print("Items in landingData:", len(items))
    for it in items[:10]:
        for v in it.get('variants', []):
            name = v.get('name', '')
            p = float(v.get('price') or 0)
            dp = float(v.get('discountedSalesPrice') or p)
            pct = v.get('discountPercentage') or 0
            imgs = v.get('images', [])
            img = imgs[0].get('src').replace('{size}', '600/600/') if imgs else ''
            print(f"Product: {name[:40]} | P: {p} | DP: {dp} | Pct: {pct}% | Img: {img}")
