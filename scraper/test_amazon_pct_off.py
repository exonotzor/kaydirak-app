import requests
import urllib3
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = 'https://www.amazon.com.tr/s?k=kulaklik&pct-off=50-'
r = requests.get(url, headers=headers, verify=False, timeout=8)
print('Amazon pct-off status:', r.status_code, 'Len:', len(r.text))

soup = BeautifulSoup(r.text, 'html.parser')
# Find search result items
cards = soup.select('div[data-component-type="s-search-result"]')
print(f"Total search result cards: {len(cards)}")

for c in cards[:5]:
    asin = c.get('data-asin')
    t = c.select_one('h2 span')
    title = t.get_text().strip() if t else 'No Title'
    
    # Check for strike price
    strike_elem = c.select_one('.a-text-price .a-offscreen')
    strike_price = strike_elem.get_text().strip() if strike_elem else None
    
    # Check for sale price
    sale_elem = c.select_one('.a-price .a-offscreen')
    sale_price = sale_elem.get_text().strip() if sale_elem else None
    
    # Check for discount percentage
    disc_elem = c.select_one('span[class*="discount"], [data-a-badge-color]')
    disc_badge = disc_elem.get_text().strip() if disc_elem else None
    
    print(f"ASIN: {asin}")
    print(f"  Title: {title[:40]}")
    print(f"  Strike: {strike_price} | Sale: {sale_price} | Badge: {disc_badge}")
