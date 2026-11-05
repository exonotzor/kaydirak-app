import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = 'https://www.amazon.com.tr/deals'
r = requests.get(url, headers=headers, verify=False, timeout=10)
print('Deals page status:', r.status_code)
print('Length:', len(r.text))

# Search for deals widget or json
soup = BeautifulSoup(r.text, 'html.parser')
print('Title:', soup.title.string if soup.title else 'None')

# Check for deal items
deals = re.findall(r'(\d+%\s*indirim|%\d+\s*indirim|-%[0-9]+)', r.text, re.IGNORECASE)
print('Found discount badges on deals page:', len(deals), deals[:10])

# Check for ASINs on deals page
asins = set(re.findall(r'/dp/([A-Z0-9]{10})', r.text))
print(f"Found {len(asins)} product ASINs on deals page.")
