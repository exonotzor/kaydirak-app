import json
from curl_cffi import requests
import re
import sys
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('scraper/amazon_verified_deals.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Loaded {len(items)} items from amazon_verified_deals.json")

live_verified = []
for i, it in enumerate(items):
    asin = it.get('asin') or it.get('id', '').replace('amz-', '')
    if not asin or len(asin) != 10:
        continue
    url = f"https://www.amazon.com.tr/dp/{asin}"
    try:
        r = requests.get(url, impersonate='chrome120', timeout=8, verify=False)
        if r.status_code != 200:
            continue
        
        is_404 = ('Sayfa Bulunamadı' in r.text) or ('dogs of amazon' in r.text.lower()) or ('köpek' in r.text.lower())
        if is_404:
            continue
            
        is_out = ('Şu anda mevcut değil' in r.text) or ('Temporarily out of stock' in r.text)
        if is_out:
            continue
            
        # Extract title
        m_title = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', r.text, re.DOTALL)
        if not m_title:
            continue
        real_title = m_title.group(1).strip()
        if len(real_title) < 5:
            continue
            
        # Clean title
        it['title'] = real_title
        it['productUrl'] = url
        it['asin'] = asin
        it['id'] = f"amz-{asin}"
        
        # Check image
        if not it.get('imageUrl') or 'amazon' not in it.get('imageUrl', ''):
            m_img = re.search(r'https://m\.media-amazon\.com/images/I/[^"\']+\.jpg', r.text)
            if m_img:
                it['imageUrl'] = m_img.group(0)
                
        live_verified.append(it)
        print(f"[{len(live_verified)}/{i+1}] LIVE & IN-STOCK: [{it.get('category')}] %{it.get('discountRate')} | {real_title[:45]} | {url}")
    except Exception as e:
        pass
    time.sleep(0.2)

print(f"\nTotal live & in-stock Amazon deals: {len(live_verified)}")
with open('scraper/amazon_strictly_live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(live_verified, f, ensure_ascii=False, indent=2)

from collections import Counter
c = Counter(x.get('category') for x in live_verified)
print("Categories:", c)
