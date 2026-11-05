import requests
import urllib3
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = 'https://www.pazarama.com/kulakliklar-k-kategori'
r = requests.get(url, headers=headers, verify=False, timeout=8)
print('Pazarama status:', r.status_code, 'Len:', len(r.text))

soup = BeautifulSoup(r.text, 'html.parser')
# Find scripts with data
for s in soup.find_all('script'):
    txt = s.string or ''
    if 'product' in txt.lower() and ('price' in txt.lower() or 'fiyat' in txt.lower()):
        print(f"Found script len: {len(txt)}, snippet: {repr(txt[:150])}")

# Check price regex in text
prices = re.findall(r'(\d+[\.,]\d{2}\s*(?:TL|₺))', r.text)
print("Prices in page text:", prices[:10])
