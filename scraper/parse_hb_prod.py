import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()

url = "https://www.hepsiburada.com/logitech-g-g102-lightsync-rgb-oyuncu-mouse-siyah-p-HBV00000V80EP"
headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

r = requests.get(url, headers=headers, verify=False, timeout=8)
soup = BeautifulSoup(r.text, 'html.parser')

print("H1:", [h.get_text().strip() for h in soup.find_all('h1')])

# Check for JSON-LD or Next data or window data
for s in soup.find_all('script'):
    txt = s.string or ''
    if '__INITIAL_STATE__' in txt or 'productModel' in txt or 'productDetail' in txt:
        print(f"Found state script! len={len(txt)}, snippet={repr(txt[:200])}")

# Let's inspect LD+JSON
for s in soup.find_all('script', type='application/ld+json'):
    try:
        data = json.loads(s.string)
        print("LD JSON type:", data.get('@type') if isinstance(data, dict) else [x.get('@type') for x in data if isinstance(x, dict)])
        if isinstance(data, dict) and data.get('@type') == 'Product':
            print("  Product name:", data.get('name'))
            print("  Offers:", data.get('offers'))
    except Exception as e:
        pass
