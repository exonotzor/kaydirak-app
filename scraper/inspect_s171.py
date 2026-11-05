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
s171 = scripts[171]

# Search for deal objects in s171
blobs = re.findall(r'(\{[^{}]*"asin"[^{}]*\})', s171)
print(f"Found {len(blobs)} asin blobs in Script 171")
if blobs:
    print("Sample blob:", blobs[0][:300])
