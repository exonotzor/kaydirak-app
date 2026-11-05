from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import sys
import json

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

url = 'https://www.amazon.com.tr/s?k=kulaklik&i=electronics'
r = requests.get(url, impersonate='chrome120', timeout=10, verify=False)
soup = BeautifulSoup(r.text, 'html.parser')

items = soup.select('div[data-asin]')
print(f"Total div[data-asin]: {len(items)}")

deals = []
for it in items:
    asin = it.get('data-asin')
    if not asin:
        continue
    
    # Title
    h2 = it.select_one('h2')
    title = h2.get_text().strip() if h2 else None
    if not title:
        continue
        
    # Image
    img = it.select_one('img.s-image')
    img_url = img.get('src') if img else None
    
    # Prices
    price_whole = it.select_one('.a-price-whole')
    price_fraction = it.select_one('.a-price-fraction')
    if not price_whole:
        continue
    p_str = price_whole.get_text().replace('.', '').replace(',', '').strip()
    f_str = price_fraction.get_text().strip() if price_fraction else '00'
    try:
        sale_price = float(f"{p_str}.{f_str}")
    except Exception:
        continue
        
    # Strikethrough price
    strike = it.select_one('.a-text-price span[aria-hidden="true"], .a-text-price .a-offscreen')
    orig_price = None
    if strike:
        st_text = strike.get_text().strip()
        m = re.search(r'((?:\d{1,3}\.)*\d+,\d{2})', st_text)
        if m:
            try:
                orig_price = float(m.group(1).replace('.', '').replace(',', '.'))
            except Exception:
                pass
                
    if orig_price and orig_price > sale_price:
        rate = round(((orig_price - sale_price) / orig_price) * 100)
        deals.append({
            'asin': asin,
            'title': title,
            'sale_price': sale_price,
            'orig_price': orig_price,
            'discountRate': rate,
            'img_url': img_url,
            'url': f"https://www.amazon.com.tr/dp/{asin}"
        })

print(f"Found {len(deals)} deals with strikethrough prices:")
for d in deals[:10]:
    print(f"  ASIN: {d['asin']} | %{d['discountRate']} | {d['orig_price']} -> {d['sale_price']} | {d['title'][:50]}")
