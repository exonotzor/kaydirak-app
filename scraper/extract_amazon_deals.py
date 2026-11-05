import re
import json

with open("scraper/amazon_deals_blob.js", "r", encoding="utf-8") as f:
    content = f.read()

# Let's see what JavaScript variable or function call this JSON is passed to
idx = content.find('"dealDetails"')
start = content.rfind('JSON.parse(', 0, idx)
if start != -1:
    print("Found JSON.parse at", start)
else:
    # let's find the outermost '{' or '[' before idx
    print("Looking for assignment before dealDetails...")
    # let's look for '= {'
    matches = list(re.finditer(r'=\s*(\{)', content[:idx]))
    if matches:
        last_m = matches[-1]
        print(f"Last assignment at {last_m.start()}: {content[last_m.start():last_m.start()+50]}")

# Let's find all ASINs and their deals
# We can regex match deal blocks!
# Each deal block has:
# "priceToPay":{..."price":"..."...}
# "basisPrice":{..."price":"..."...}
# "asin":"([A-Z0-9]{10})"
deal_blocks = re.split(r'\}\s*,\s*\{"dealDetails"', content)
print(f"Split by dealDetails produced {len(deal_blocks)} blocks")

for i, block in enumerate(deal_blocks[:5]):
    asin_m = re.search(r'"asin"\s*:\s*"([A-Z0-9]{10})"', block)
    price_m = re.search(r'"priceToPay"\s*:\s*\{[^}]*"price"\s*:\s*"([^"]+)"', block)
    basis_m = re.search(r'"basisPrice"\s*:\s*\{[^}]*"price"\s*:\s*"([^"]+)"', block)
    title_m = re.search(r'"title"\s*:\s*"([^"]+)"', block)
    img_m = re.search(r'"primaryImage"\s*:\s*\{[^}]*"url"\s*:\s*"([^"]+)"', block) or re.search(r'"url"\s*:\s*"(https://m\.media-amazon\.com/images/I/[^"]+)"', block)
    
    print(f"\nBlock {i}:")
    print(f"  ASIN:  {asin_m.group(1) if asin_m else 'None'}")
    print(f"  Price: {price_m.group(1) if price_m else 'None'}")
    print(f"  Basis: {basis_m.group(1) if basis_m else 'None'}")
    print(f"  Title: {title_m.group(1) if title_m else 'None'}")
    print(f"  Img:   {img_m.group(1) if img_m else 'None'}")
