import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
}

# 1. Test Idefix
print("--- TEST 1: IDEFIX ---")
url_idefix = 'https://www.idefix.com/us-polo-assn-kadin-beyaz-uzun-kollu-basic-gomlek-50324791-vr013-p-26711236'
r = requests.get(url_idefix, headers=headers, verify=False, timeout=10)
print('Status:', r.status_code)
if r.status_code == 200:
    # Check Next.js __NEXT_DATA__
    soup = BeautifulSoup(r.text, 'html.parser')
    s = soup.find('script', id='__NEXT_DATA__')
    if s and s.string:
        d = json.loads(s.string)
        pdp = d.get('props', {}).get('pageProps', {}).get('product', {})
        if not pdp:
            pdp = d.get('props', {}).get('pageProps', {}).get('initialState', {}).get('pdp', {}).get('product', {})
        print('PDP title:', pdp.get('name'))
        for v in pdp.get('variants', []):
            print('Variant:', v.get('name'), 'price:', v.get('price'), 'discounted:', v.get('discountedSalesPrice'))

# 2. Test Amazon TR
print("\n--- TEST 2: AMAZON TR ---")
url_amz = 'https://www.amazon.com.tr/dp/B0725YBH5N'
r = requests.get(url_amz, headers=headers, verify=False, timeout=10)
print('Amazon Status:', r.status_code)
soup = BeautifulSoup(r.text, 'html.parser')
title = soup.find('span', id='productTitle')
print('Title:', title.get_text().strip() if title else 'None (Blocked or Captcha)')
price_whole = soup.find('span', class_='a-price-whole')
price_fraction = soup.find('span', class_='a-price-fraction')
print('Price:', f"{price_whole.get_text().strip()},{price_fraction.get_text().strip()}" if price_whole and price_fraction else 'None')
