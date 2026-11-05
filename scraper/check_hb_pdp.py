import requests
import urllib3
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = "https://www.hepsiburada.com/redmi-buds-6-play-siyah-kulakici-kulaklik-tws-xiaomi-turkiye-garantili-p-HBCV000072PXK3"
r = requests.get(url, headers=headers, verify=False, timeout=8)
print("Status:", r.status_code, "Final URL:", r.url)

soup = BeautifulSoup(r.text, 'html.parser')
h1 = soup.find('h1')
print("H1 Title:", h1.get_text().strip() if h1 else 'None')

# Look for price elements
for p in soup.select('[data-test-id*="price"], [class*="price"], [class*="Price"], [data-bind*="price"]'):
    txt = p.get_text().strip()
    if 'TL' in txt or '₺' in txt or re.search(r'\d+,\d{2}', txt):
        classes = p.get('class')
        testid = p.get('data-test-id')
        print(f"Elem testid={testid} class={classes} -> {repr(txt[:60])}")
