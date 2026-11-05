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
html = r.text

print(f"Loaded {len(html)} bytes.")

# Search for Spigen
for m in re.finditer(r'(Spigen[^\<\>\"\n]{10,80})', html, re.IGNORECASE):
    print('Found product mention:', m.group(1))
    break

# Search for any TL prices in HTML
prices = re.findall(r'(\d+[\.,]\d{2}\s*(?:TL|₺)|(?:TL|₺)\s*\d+[\.,]\d{2})', html)
print('Found TL matches:', prices[:10])

# Search for raw numbers near price keywords
for m in re.finditer(r'(?:price|priceToPay|apexPrice|corePrice)[^\<\>]{0,100}?(\d+[\.,]\d{2})', html, re.IGNORECASE):
    print('Price near keyword:', m.group(0)[:80])
