import json
from curl_cffi import requests
import re
import sys
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

amz_deals = [d for d in deals if d['store'] == 'Amazon TR']
print(f"Testing all {len(amz_deals)} Amazon deals with curl_cffi...")

results = []
for i, d in enumerate(amz_deals):
    url = d['productUrl']
    try:
        r = requests.get(url, impersonate='chrome120', timeout=10, verify=False)
        m = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', r.text, re.DOTALL)
        p_title = m.group(1).strip() if m else None
        
        is_404 = ('Sayfa Bulunamadı' in r.text) or ('dogs of amazon' in r.text.lower()) or ('köpek' in r.text.lower()) or r.status_code == 404
        is_out_of_stock = ('Şu anda mevcut değil' in r.text) or ('Temporarily out of stock' in r.text)
        
        status = '404_NOT_FOUND' if is_404 else ('OUT_OF_STOCK' if is_out_of_stock else 'OK')
        results.append({
            'index': i + 1,
            'asin': url.split('/')[-1],
            'url': url,
            'status': status,
            'catalog_title': d['title'],
            'actual_title': p_title,
            'http_status': r.status_code
        })
        print(f"[{i+1:2d}/40] {status} | HTTP {r.status_code} | {url} | Actual: {p_title[:40] if p_title else 'N/A'}")
    except Exception as e:
        print(f"[{i+1:2d}/40] ERROR: {e} | {url}")
        results.append({
            'index': i + 1,
            'url': url,
            'status': f'ERROR: {e}'
        })
    time.sleep(0.3)

with open('scraper/amz_test_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nDone testing all Amazon deals!")
