import requests
import urllib3
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

asins = ['B0D8WP1RLR', 'B0HCJRPB37', 'B0DSXDR4HY', 'B07P1T5H5L', 'B0DKP58P2P']

for asin in asins:
    url = f"https://www.amazon.com.tr/gp/aw/d/{asin}"
    r = requests.get(url, headers=headers, verify=False, timeout=6)
    soup = BeautifulSoup(r.text, 'html.parser')
    t = soup.select_one('#title, #productTitle, h1')
    title = t.get_text().strip() if t else ''
    
    # Let's inspect all .a-price elements
    prices = []
    for p in soup.select('.a-price'):
        txt = p.get_text().strip().replace('\n', ' ')
        classes = p.get('class', [])
        is_strike = 'a-text-price' in classes or p.get('data-a-strike') == 'true'
        m = re.search(r'((?:\d{1,3}\.)*\d+,\d{2})', txt)
        if m:
            val = float(m.group(1).replace('.', '').replace(',', '.'))
            prices.append((val, 'STRIKE' if is_strike else 'SALE'))
            
    print(f"\nASIN {asin}: {title[:40]}")
    print(f"Parsed .a-price: {prices}")
