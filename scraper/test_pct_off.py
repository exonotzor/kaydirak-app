from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

url = 'https://www.amazon.com.tr/s?k=kulaklik&pct-off=20-'
r = requests.get(url, impersonate='chrome120', timeout=10, verify=False)
soup = BeautifulSoup(r.text, 'html.parser')
cards = soup.select('div[data-component-type="s-search-result"]')
print(f"Cards found: {len(cards)}")

deals = []
for c in cards:
    asin = c.get('data-asin')
    if not asin:
        continue
    t = c.select_one('h2 span')
    title = t.get_text().strip() if t else ''
    strike_el = c.select_one('.a-text-price .a-offscreen')
    sale_el = c.select_one('.a-price:not(.a-text-price) .a-offscreen')
    img_el = c.select_one('img.s-image')
    
    if strike_el and sale_el and img_el:
        st_text = strike_el.get_text().strip()
        sa_text = sale_el.get_text().strip()
        img_url = img_el.get('src')
        print(f"ASIN: {asin} | Strike: {st_text} | Sale: {sa_text} | Title: {title[:40]}")
        deals.append(asin)

print(f"Total valid deals found on 1 page: {len(deals)}")
