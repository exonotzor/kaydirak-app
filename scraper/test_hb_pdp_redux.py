import requests
import urllib3
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

pdp_url = "https://www.hepsiburada.com/redmi-buds-6-play-siyah-kulakici-kulaklik-tws-xiaomi-turkiye-garantili-p-HBCV000072PXK3"
r = requests.get(pdp_url, headers=headers, verify=False, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
s = soup.find('script', id='reduxStore')
if s and s.string:
    data = json.loads(s.string)
    prod = data.get('productState', {}).get('product', {})
    print("Product title:", prod.get('name'))
    listings = prod.get('listings', [])
    print("Total listings:", len(listings))
    if listings:
        l = listings[0]
        print("Listing 0 keys:", list(l.keys()))
        print("Price info:", l.get('price'), "Original price:", l.get('originalPrice'), "Discount:", l.get('discountRate'))
    # Also check variantList or defaultVariant
    for k in ['price', 'originalPrice', 'discountRate', 'currentPrice']:
        if k in prod:
            print(f"prod.{k} = {prod.get(k)}")
