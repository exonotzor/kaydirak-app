import re
import json

with open("scraper/amazon_deals_blob.js", "r", encoding="utf-8") as f:
    text = f.read()

# find ASINs with clothing/fashion words
asins = set(re.findall(r'"asin"\s*:\s*"([B0-9A-Z]{10})"', text))
print(f"Total ASINs in amazon_deals_blob.js: {len(asins)}")

for a in sorted(asins)[:30]:
    # find chunk around this asin
    idx = text.find(a)
    chunk = text[max(0, idx-100):min(len(text), idx+300)]
    print(a, '->', chunk.replace('\n', ' ')[:100])
