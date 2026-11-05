import re
import json

with open('scraper/amz_deals.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Look for embedded deal data in scripts
for m in re.finditer(r'<script\b[^>]*>(.*?)</script>', html, re.DOTALL):
    s = m.group(1)
    if 'dealDetails' in s or 'dealPrice' in s or 'dealTitle' in s or 'widgetState' in s:
        print(f"Found candidate script! len: {len(s)}")
        # Look for JSON arrays of deals
        for match in re.finditer(r'\{[^{}]*"dealId"[^{}]*\}', s):
            print("  Deal snippet:", match.group(0)[:150])

# Look for widget data blobs
for m in re.finditer(r'data-a-state="([^"]*)"', html):
    state_name = m.group(1)
    print("Found a-state:", state_name)
