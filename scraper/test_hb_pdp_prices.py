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
data = json.loads(s.string)
prod = data.get('productState', {}).get('product', {})
listings = prod.get('listings', [])
for i, l in enumerate(listings[:2]):
    print(f"--- LISTING {i} ---")
    print("originalPrice:", l.get('originalPrice'))
    print("prices:", l.get('prices'))
    print("discountRate:", l.get('discountRate'))
    print("minimumPrice:", l.get('minimumPrice'))
