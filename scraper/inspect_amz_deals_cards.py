from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import sys
import json

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

url = 'https://www.amazon.com.tr/deals'
r = requests.get(url, impersonate='chrome120', timeout=10, verify=False)
soup = BeautifulSoup(r.text, 'html.parser')

links = soup.select('a[href*="/dp/"]')
print(f"Total /dp/ links: {len(links)}")

seen_asins = set()
for a in links:
    href = a.get('href', '')
    m = re.search(r'/dp/([B0-9A-Z]{10})', href)
    if not m:
        continue
    asin = m.group(1)
    if asin in seen_asins:
        continue
    seen_asins.add(asin)
    
    # Try finding parent card
    card = a.find_parent('div', class_=re.compile(r'Deal|Card|Item|Grid', re.I)) or a.parent
    text = card.get_text(separator=' | ').strip() if card else ''
    img = a.find('img') or (card.find('img') if card else None)
    img_src = img.get('src') if img else None
    
    print(f"\n--- ASIN: {asin} ---")
    print(f"URL: https://www.amazon.com.tr/dp/{asin}")
    print(f"Image: {img_src}")
    print(f"Text: {text[:200]}")
    if len(seen_asins) >= 5:
        break
