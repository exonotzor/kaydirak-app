import requests
import urllib3
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

r = requests.get('https://www.amazon.com.tr/gp/aw/d/B0D21L6NJ7', headers=headers, verify=False)
soup = BeautifulSoup(r.text, 'html.parser')

print('HTML <title> tag:', soup.title.string if soup.title else 'None')

# Check title elements
t = soup.select_one('#title') or soup.select_one('#productTitle') or soup.select_one('h1')
print('Found Title:', t.get_text().strip() if t else 'None')

# Search for prices in text or scripts
print('\n--- ALL PRICE CANDIDATES ---')
for p in soup.select('.a-price, [class*="price"], [id*="price"]'):
    txt = p.get_text().strip()
    if 'TL' in txt or '₺' in txt or re.search(r'\d+,\d{2}', txt):
        print(f"Price elem: id={p.get('id')} class={p.get('class')} -> {repr(txt[:60])}")

# Check LD+JSON
print('\n--- LD+JSON ---')
import json
for s in soup.find_all('script', type='application/ld+json'):
    try:
        data = json.loads(s.string)
        print('LD+JSON:', data)
    except Exception:
        pass
