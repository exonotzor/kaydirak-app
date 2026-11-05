from curl_cffi import requests
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

headers = {'Accept-Language': 'tr-TR,tr;q=0.9'}
asins = ['B0FZ9X5RBC', 'B08GPCGVBY', 'B0GHR4L88D', 'B0CX92GNCX', 'B0F7J2DJ8X', 'B0017LSY88', 'B003M6AL5E', 'B003M6AM0S', 'B003M6AM08']

for a in asins:
    url = f"https://www.amazon.com.tr/dp/{a}"
    try:
        r = requests.get(url, impersonate='chrome120', timeout=6, verify=False, headers=headers)
        is_out = ('Şu anda mevcut değil' in r.text) or ('Temporarily out of stock' in r.text)
        is_404 = ('Sayfa Bulunamadı' in r.text) or ('dogs of amazon' in r.text.lower())
        m = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', r.text, re.DOTALL)
        title = m.group(1).strip() if m else 'N/A'
        status = '404' if is_404 else ('OUT' if is_out else 'OK')
        print(f"{a}: {status} | HTTP {r.status_code} | {title[:50]}")
    except Exception as e:
        print(f"{a}: ERROR {e}")
