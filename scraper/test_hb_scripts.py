import requests
import re
import urllib3
import json
urllib3.disable_warnings()

headers = {'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)'}
url = 'https://www.hepsiburada.com/bioderma-photoderm-spot-spf50-yuksek-korumali-yuz-ve-vucut-gunes-kremi-150-ml-pm-HB00000IMEJ6'
r = requests.get(url, headers=headers, verify=False, timeout=8)

# Check script tags
scripts = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)
print("Total scripts:", len(scripts))

for s in scripts:
    if 'price' in s.lower() or 'original' in s.lower() or 'schema.org' in s.lower() or 'product' in s.lower():
        if len(s) < 2000:
            print("--- SCRIPT MATCH ---")
            print(s[:500])

# Check for JSON in HTML
matches = re.findall(r'(\{[^{}]*"price"[^{}]*\})', r.text)
print("Price json snippets:", len(matches))
for m in matches[:5]:
    print(m)
