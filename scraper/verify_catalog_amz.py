import json
import sys
from curl_cffi import requests

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

amz_deals = [d for d in deals if d['store'] == 'Amazon TR']
print(f'Checking {len(amz_deals)} Amazon TR deals from live_deals.json...\n')

s = requests.Session()
success = 0
failed = 0

for i, d in enumerate(amz_deals, 1):
    url = d['productUrl']
    try:
        r = s.get(url, impersonate='chrome120', timeout=15, verify=False)
        html = r.text
        is_404 = 'sayfa bulunamadı' in html.lower() or 'dogs of amazon' in html.lower() or 'page not found' in html.lower() or r.status_code == 404
        out_of_stock = 'Şu anda mevcut değil' in html
        has_title = 'id="productTitle"' in html or '<title>' in html
        
        status = 'OK'
        if is_404:
            status = '404_NOT_FOUND'
            failed += 1
        elif out_of_stock:
            status = 'OUT_OF_STOCK'
            failed += 1
        elif r.status_code == 200:
            success += 1
        else:
            status = f'HTTP_{r.status_code}'
            failed += 1
            
        print(f'{i:02d}. [{status}] [{d["category"]}] {d["id"]} | {d["title"][:45]} | {url}')
    except Exception as e:
        print(f'{i:02d}. [ERROR] {d["id"]}: {e}')
        failed += 1

print(f'\nSummary: {success}/{len(amz_deals)} verified active & in-stock, {failed} failed.')
