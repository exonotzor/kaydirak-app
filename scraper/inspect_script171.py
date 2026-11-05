import re
import json

with open("scraper/parse_amazon_deals.py", "r") as f:
    # let's write a script that inspects script 171
    pass

import urllib.request

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

url = "https://www.amazon.com.tr/deals"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

script_blobs = re.findall(r'<script\b[^>]*>(.*?)</script>', html, re.DOTALL)
for i, blob in enumerate(script_blobs):
    if 'dealDetails' in blob or 'dealItems' in blob:
        print(f"--- Script {i} ---")
        # search for JSON objects
        matches = re.findall(r'(\{"dealID".*?\})', blob)
        print(f"Matches for dealID: {len(matches)}")
        if not matches:
            # find keywords
            for word in ['dealDetails', 'dealItems', 'itemDetails', 'primaryImage']:
                pos = blob.find(word)
                if pos != -1:
                    print(f"Keyword {word} at {pos}:")
                    print(blob[max(0, pos-100):pos+300])
