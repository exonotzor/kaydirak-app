import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url_hb = 'https://www.hepsiburada.com/logitech-g-g102-lightsync-rgb-oyuncu-mouse-siyah-p-HBV00000V80EP'
r = requests.get(url_hb, headers=headers, verify=False, timeout=8)
print('HB status:', r.status_code)
if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    for s in soup.find_all('script', type='application/ld+json'):
        try:
            d = json.loads(s.string)
            if d.get('@type') == 'Product':
                print('HB LD Product:', d.get('name'))
                print('HB LD Offers:', d.get('offers'))
        except Exception:
            pass
    # check html prices
    prices = re.findall(r'(\d+[\.,]\d{2}\s*(?:TL|₺))', r.text)
    print('HB prices found:', prices[:5])
