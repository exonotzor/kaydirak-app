import re
from curl_cffi import requests
import json
import time
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open("scraper/amazon_deals_blob.js", "r", encoding="utf-8") as f:
    text = f.read()

asins = list(set(re.findall(r'"asin"\s*:\s*"([B0-9A-Z]{10})"', text)))
print(f"Total ASINs in blob: {len(asins)}")

headers = {'Accept-Language': 'tr-TR,tr;q=0.9'}

live_blob = []
for a in asins:
    url = f"https://www.amazon.com.tr/dp/{a}"
    try:
        r = requests.get(url, impersonate='chrome120', timeout=6, verify=False, headers=headers)
        if r.status_code == 200 and 'Şu anda mevcut değil' not in r.text and 'Sayfa Bulunamadı' not in r.text:
            m = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', r.text, re.DOTALL)
            if m:
                title = m.group(1).strip()
                m_img = re.search(r'https://m\.media-amazon\.com/images/I/[^"\']+\.jpg', r.text)
                img = m_img.group(0) if m_img else ''
                print(f"LIVE: {a} | {title[:50]} | {url}")
                live_blob.append({'asin': a, 'title': title, 'url': url, 'img': img})
    except Exception:
        pass
    time.sleep(0.15)

with open('scraper/live_blob_asins.json', 'w', encoding='utf-8') as f:
    json.dump(live_blob, f, ensure_ascii=False, indent=2)

print(f"Total live in-stock from blob: {len(live_blob)}")
