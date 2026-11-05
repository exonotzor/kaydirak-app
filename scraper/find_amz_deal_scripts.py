from curl_cffi import requests
import re
import sys
import json

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

url = 'https://www.amazon.com.tr/deals'
r = requests.get(url, impersonate='chrome120', timeout=10, verify=False)

scripts = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)
print(f"Total scripts: {len(scripts)}")
for i, s in enumerate(scripts):
    if 'dealDetails' in s or 'dealPrice' in s or 'widgetData' in s or 'asin' in s.lower():
        print(f"Script {i} len {len(s)}: {s[:200]}...")
