import re
import json

with open('scraper/amz_deals_script.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Look for ASINs
asins = set(re.findall(r'B0[A-Z0-9]{8}', text))
print(f"ASINs found in deals script: {len(asins)}")
print(list(asins)[:10])

# Look for JSON structures in text
for m in re.finditer(r'\{[^{}]*"title"[^{}]*\}', text):
    print("Found title match:", m.group(0)[:120])
