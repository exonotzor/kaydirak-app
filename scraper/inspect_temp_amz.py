from bs4 import BeautifulSoup
import re

with open('scraper/temp_amz.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
title = soup.find('span', id='productTitle')
print('Title:', title.get_text().strip() if title else 'None')

# Check availability
avail = soup.find('div', id='availability')
if avail:
    print('Availability:', avail.get_text().strip())

# Check prices
prices = []
for p in soup.select('.a-price .a-offscreen, .priceToPay .a-offscreen, .apexPriceToPay .a-offscreen, .a-color-price'):
    txt = p.get_text().strip()
    if txt and ('TL' in txt or '₺' in txt or any(c.isdigit() for c in txt)):
        prices.append(txt)

print('Found prices:', prices)

# Check strikethrough (original) price
orig_prices = []
for p in soup.select('.a-price[data-a-strike="true"] .a-offscreen, .basisPrice .a-offscreen'):
    txt = p.get_text().strip()
    if txt:
        orig_prices.append(txt)

print('Found original (strike) prices:', orig_prices)
