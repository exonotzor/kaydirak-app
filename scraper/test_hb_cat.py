import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = "https://www.hepsiburada.com/kulakliklar-c-2141?siralama=coksatan"
r = requests.get(url, headers=headers, verify=False, timeout=8)
print("Status:", r.status_code, "Final URL:", r.url)

soup = BeautifulSoup(r.text, 'html.parser')
print("Title:", soup.title.get_text() if soup.title else 'No Title')

# Search for products in LD+JSON or scripts
found_items = []
for s in soup.find_all('script'):
    txt = s.string or ''
    if '__INITIAL_STATE__' in txt or 'products' in txt:
        if 'productName' in txt or 'price' in txt:
            print("Found script containing products! len:", len(txt))
            # try to find json
            m = re.search(r'__INITIAL_STATE__\s*=\s*(\{.*?\});', txt, re.DOTALL)
            if m:
                print("Found __INITIAL_STATE__ match!")
            m2 = re.search(r'window\.PRODUCT_LIST\s*=\s*(\{.*?\});', txt, re.DOTALL)
            if m2:
                print("Found PRODUCT_LIST match!")

# Let's inspect product cards in HTML
cards = soup.select('li[id*="li-"], [data-test-id="product-card"], li[class*="productListContent"]')
print(f"Product cards in DOM: {len(cards)}")
for c in cards[:3]:
    print("Card snippet:", c.get_text()[:100].replace('\n', ' '))
