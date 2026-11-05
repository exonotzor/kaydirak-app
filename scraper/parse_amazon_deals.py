import urllib.request
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
}

url = "https://www.amazon.com.tr/deals"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

print(f"Amazon Deals HTML length: {len(html)}")

# Find deal components or data blobs
# Amazon deals often store deal data in JSON inside script tags or data attributes
script_blobs = re.findall(r'<script\b[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"Found {len(script_blobs)} script tags")

for i, blob in enumerate(script_blobs):
    if 'dealDetails' in blob or 'dealItems' in blob or 'widgetConfig' in blob:
        print(f"Script {i} contains deal data! Length: {len(blob)}")
        # Print a snippet
        print(blob[:300])

# Also check for data-deal or product cards
asins = set(re.findall(r'/dp/([B0-9A-Z]{10})', html))
print(f"Found {len(asins)} distinct ASINs in deals page: {list(asins)[:10]}")
