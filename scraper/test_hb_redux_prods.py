import requests
import urllib3
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = "https://www.hepsiburada.com/ara?q=kulaklik"
r = requests.get(url, headers=headers, verify=False, timeout=10)

soup = BeautifulSoup(r.text, 'html.parser')
s = soup.find('script', id='reduxStore')
data = json.loads(s.string)
prods = data.get('searchState', {}).get('searchProductArray', [])
print(f"Total products: {len(prods)}")
for p in prods[:5]:
    variants = p.get('variantList', [])
    for v in variants:
        print("--- VARIANT ---")
        print("Name:", v.get('name'))
        print("Url:", v.get('url'))
        print("Price dict:", v.get('price'))
        print("Images:", v.get('images', [])[:1])
