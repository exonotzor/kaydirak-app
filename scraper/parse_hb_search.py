import requests
import urllib3
import re
import json

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = "https://www.hepsiburada.com/ara?q=kulaklik"
r = requests.get(url, headers=headers, verify=False, timeout=10)

# Search for product listings in the script
# Common Hepsiburada patterns: window.__INITIAL_STATE__ or products or productList
matches = re.findall(r'(\{"productId"[^}]+"price":[^}]+\})', r.text)
print("ProductId matches:", len(matches))
if matches:
    print("Match 1:", matches[0][:300])

# Look for discountRate > 0
discount_matches = re.findall(r'\{[^{}]*"discountRate":([1-9]\d*)[^{}]*\}', r.text)
print("Discounts found:", len(discount_matches), discount_matches[:10])

# Let's inspect where product items are
# Let's find script that contains productList
for s in re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL):
    if 'productList' in s or 'products' in s:
        print("Found script with products, len:", len(s))
        # Let's extract any json object
        m = re.search(r'products\s*:\s*(\[[^\]]+\])', s)
        if m:
            print("Found products array!")
            break
