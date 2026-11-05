import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor
import sys

urllib3.disable_warnings()
headers = {'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)'}

with open('scraper/hepsiburada_verified_deals.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)

print(f"Current HB deals: {len(existing)}")

seen_urls = set(x['productUrl'] for x in existing)

targets = [
    ('Teknoloji', 'philips tras makinasi'),
    ('Teknoloji', 'sandisk extreme ssd'),
    ('Moda', 'crocs terlik'),
    ('Moda', 'columbia polar ceket'),
    ('Ev & Yaşam', 'contigo termos'),
    ('Ev & Yaşam', 'arcelik kahve makinasi'),
    ('Kozmetik', 'oral-b dis fircasi'),
    ('Kozmetik', 'flormar oje seti')
]

candidates = []
for cat, q in targets:
    url = f"https://www.hepsiburada.com/ara?q={requests.utils.quote(q)}"
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=6)
        if r.status_code == 200:
            found = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', r.text)
            for u in list(dict.fromkeys(found))[:8]:
                full_url = 'https://www.hepsiburada.com' + u.split('?')[0]
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    candidates.append((cat, full_url))
    except Exception as e:
        print(f"Error {q}: {e}")

print(f"Candidates to verify: {len(candidates)}")

def verify(item):
    cat, url = item
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=6)
        if r.status_code != 200 or len(r.text) < 15000:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
        h1 = soup.find('h1')
        title = h1.get_text().strip() if h1 else ''
        if not title or len(title) < 5 or 'Güvenlik' in title:
            return None
        p_boxes = soup.select('span[data-test-id="variant-box-price"], [data-test-id="default-price"], del, [class*="Price"], [class*="price"]')
        prices = []
        for pb in p_boxes:
            for m in re.findall(r'((?:\d{1,3}\.)*\d+,\d{2})', pb.get_text().strip()):
                try:
                    prices.append(float(m.replace('.', '').replace(',', '.')))
                except:
                    pass
        prices = sorted(list(set(prices)))
        if len(prices) >= 2:
            p_sale = prices[0]
            for p in prices[1:]:
                if 1.15 <= (p / p_sale) <= 3.5:
                    rate = round(((p - p_sale) / p) * 100)
                    imgs = re.findall(r'https://productimages\.hepsiburada\.net/s/[^\s"\'<>]+\.jpg', r.text)
                    img_url = imgs[0].replace('{size}', '550') if imgs else ''
                    sku_match = re.search(r'-p(?:m)?-([A-Za-z0-9]+)', url)
                    sku = sku_match.group(1) if sku_match else 'hb'
                    return {
                        'id': f"hb-{sku}",
                        'title': title,
                        'category': cat,
                        'store': 'Hepsiburada',
                        'originalPrice': p,
                        'discountedPrice': p_sale,
                        'discountRate': rate,
                        'productUrl': url,
                        'imageUrl': img_url
                    }
    except:
        pass
    return None

new_deals = []
with ThreadPoolExecutor(max_workers=15) as ex:
    for res in ex.map(verify, candidates):
        if res:
            new_deals.append(res)
            print(f"VERIFIED: [{res['category']}] %{res['discountRate']} | {res['discountedPrice']} TL (was {res['originalPrice']} TL) | {res['title'][:40]}")
            if len(new_deals) >= 6:
                break

all_hb = existing + new_deals
print(f"Total HB deals now: {len(all_hb)}")
with open('scraper/hepsiburada_verified_deals.json', 'w', encoding='utf-8') as f:
    json.dump(all_hb, f, ensure_ascii=False, indent=2)
print("Saved to scraper/hepsiburada_verified_deals.json")
