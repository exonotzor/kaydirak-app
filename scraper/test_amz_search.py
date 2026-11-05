from curl_cffi import requests
import re
import sys
import json
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

url = 'https://www.amazon.com.tr/s?k=kulaklik&i=electronics'
try:
    r = requests.get(url, impersonate='chrome120', timeout=10, verify=False)
    print('Search status:', r.status_code, 'Len:', len(r.text))
    asins = re.findall(r'data-asin="([B0-9A-Z]{10})"', r.text)
    unique_asins = [a for a in list(dict.fromkeys(asins)) if a]
    print('Found ASINs:', len(unique_asins), unique_asins[:10])
except Exception as e:
    print('Error:', e)
