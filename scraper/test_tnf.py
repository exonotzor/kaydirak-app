from curl_cffi import requests
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

headers = {'Accept-Language': 'tr-TR,tr;q=0.9'}

for a in ['B0DGLSTWRT', 'B0DGLRK7BC', 'B0DGLRPMRD', 'B0DGLRWHLX', 'B0DGLQRR3L']:
    url = f"https://www.amazon.com.tr/dp/{a}"
    r = requests.get(url, impersonate='chrome120', timeout=6, verify=False, headers=headers)
    m = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', r.text, re.DOTALL)
    title = m.group(1).strip() if m else 'N/A'
    is_out = ('Şu anda mevcut değil' in r.text) or ('Temporarily out of stock' in r.text)
    print(f"{a}: {'OUT' if is_out else 'OK'} | {title[:50]}")
