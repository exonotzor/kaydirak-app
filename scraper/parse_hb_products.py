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

# Let's extract the full JSON object containing products
match = re.search(r'products\s*:\s*(\[\{.*?\}\])\s*,\s*filters', r.text, re.DOTALL)
if not match:
    # try finding JSON in script
    for s in re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL):
        if 'productId' in s and 'variantList' in s:
            # find where array starts
            idx = s.find('"products":[')
            if idx != -1:
                print("Found products array index!")
                # Let's find matching bracket
                sub = s[idx+11:]
                bracket_count = 0
                end_idx = 0
                for i, c in enumerate(sub):
                    if c == '[':
                        bracket_count += 1
                    elif c == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_idx = i + 1
                            break
                prod_json = sub[:end_idx]
                try:
                    data = json.loads(prod_json)
                    print(f"Parsed {len(data)} products!")
                    print(json.dumps(data[0], indent=2)[:800])
                    for p in data:
                        vl = p.get('variantList', [{}])[0]
                        price_info = vl.get('price', {})
                        # check originalPrice vs price
                        orig = price_info.get('originalPrice')
                        curr = price_info.get('price')
                        disc = price_info.get('discountRate')
                        if disc and disc > 0:
                            print(f"DEAL: {p.get('name')} | Curr: {curr} | Orig: {orig} | Rate: {disc}%")
                except Exception as e:
                    print("JSON parse error:", e)
