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
soup = BeautifulSoup(r.text, 'html.parser')

# Find all elements containing 797 or 1.190 or TL
for el in soup.find_all(text=re.compile(r'797|1\.190')):
    parent = el.parent
    print(f"Parent <{parent.name}> class={parent.get('class')} testid={parent.get('data-test-id')}: {repr(el.strip())}")
    grandparent = parent.parent
    if grandparent:
        print(f"  Grandparent <{grandparent.name}> class={grandparent.get('class')} testid={grandparent.get('data-test-id')}")
