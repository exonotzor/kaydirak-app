import re
import json

with open('scraper/amz_deals.html', 'r', encoding='utf-8') as f:
    html = f.read()

for m in re.finditer(r'<script\b[^>]*>(.*?)</script>', html, re.DOTALL):
    s = m.group(1)
    if 'dealDetails' in s or 'dealPrice' in s or 'dealTitle' in s or 'widgetState' in s:
        # print first 500 chars
        print("Script snippet:", s[:500])
        with open('scraper/amz_deals_script.js', 'w', encoding='utf-8') as sf:
            sf.write(s)
        print("Saved script to scraper/amz_deals_script.js")
        break
