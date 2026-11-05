import re
import json

with open("scraper/amazon_deals_blob.js", "r", encoding="utf-8") as f:
    content = f.read()

# Let's see how many items are in this blob
# Let's find all occurrences of "priceToPay"
matches = list(re.finditer(r'"priceToPay"', content))
print(f"Total deals with priceToPay: {len(matches)}")

for i, m in enumerate(matches):
    start = max(0, m.start() - 300)
    end = min(len(content), m.start() + 1500)
    chunk = content[start:end]
    
    asin = re.search(r'"asin"\s*:\s*"([A-Z0-9]{10})"', chunk)
    price = re.search(r'"priceToPay"\s*:\s*\{[^}]*"price"\s*:\s*"([^"]+)"', chunk)
    basis = re.search(r'"basisPrice"\s*:\s*\{[^}]*"price"\s*:\s*"([^"]+)"', chunk)
    title = re.search(r'"title"\s*:\s*"([^"]+)"', chunk)
    imgs = re.findall(r'https://[^\s",]+\.(?:jpg|png)', chunk)
    
    if price and basis:
        p = float(price.group(1))
        b = float(basis.group(1))
        discount = round(((b - p) / b) * 100)
        t = title.group(1) if title else "No title"
        a = asin.group(1) if asin else "No ASIN"
        print(f"[{i}] ASIN: {a} | -%{discount} | {p} TL (was {b} TL) | {t[:40]} | Imgs: {len(imgs)}")
        if discount >= 45:
            print(f"   -> FOUND >=45% DEAL: {t} | Image: {imgs[0] if imgs else 'None'}")
