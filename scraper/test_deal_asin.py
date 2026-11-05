import subprocess
import re
from bs4 import BeautifulSoup

asin = 'B0DKP58P2P'
url = f"https://www.amazon.com.tr/dp/{asin}"
cmd = f'"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --headless=new --disable-gpu --dump-dom "{url}"'

out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
html = out.decode('utf-8', errors='ignore')

soup = BeautifulSoup(html, 'html.parser')
t = soup.select_one('#productTitle, h1')
title = t.get_text().strip() if t else 'No Title'
print(f"ASIN: {asin}")
print(f"Title: {title}")

# Check prices
prices = []
for p in soup.select('.a-price'):
    txt = p.get_text().strip().replace('\n', ' ')
    classes = p.get('class', [])
    is_strike = 'a-text-price' in classes or p.get('data-a-strike') == 'true'
    prices.append((txt, 'STRIKE' if is_strike else 'SALE'))

print("Prices:", prices)
