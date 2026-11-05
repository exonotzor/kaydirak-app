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
print("Status:", r.status_code, "Length:", len(r.text))

soup = BeautifulSoup(r.text, 'html.parser')
title = soup.find('title')
print("Title:", title.get_text() if title else 'No Title')

# Look for LD+JSON
for s in soup.find_all('script', type='application/ld+json'):
    try:
        data = json.loads(s.string)
        if isinstance(data, dict) and data.get('@type') == 'Product':
            print("Found Product in LD+JSON!")
            print("  Name:", data.get('name'))
            print("  Image:", data.get('image'))
            print("  Offers:", data.get('offers'))
    except Exception:
        pass

# Look for price spans
for p in soup.select('[data-test-id*="price"], [class*="price"], [class*="Price"]'):
    txt = p.get_text().strip()
    if 'TL' in txt or '₺' in txt:
        print(f"Price tag ({p.get('class')}): {txt[:50]}")
