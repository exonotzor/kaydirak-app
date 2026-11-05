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
print('Deals status:', r.status_code, 'Len:', len(r.text))

# Check for deal widgets or json data
deals_data = re.findall(r'data-deal-id="([^"]+)"', r.text)
print('Found deal IDs:', len(deals_data))

# Search for ASINs
asins = re.findall(r'/dp/([B0-9A-Z]{10})', r.text)
print('Found /dp/ ASINs:', len(asins), list(dict.fromkeys(asins))[:10])
