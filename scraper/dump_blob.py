import urllib.request
import re
import json

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
for blob in script_blobs:
    if 'dealDetails' in blob:
        # Find json object
        m = re.search(r'\{.*"dealDetails".*\}', blob, re.DOTALL)
        if m:
            print("Found big JSON blob, length:", len(m.group(0)))
            # Let's save it to a file so we can inspect
            with open("scraper/amazon_deals_blob.js", "w", encoding="utf-8") as out:
                out.write(blob)
            print("Saved to scraper/amazon_deals_blob.js")
            break
