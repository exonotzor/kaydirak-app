from curl_cffi import requests
import re
import sys
import json
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('backend/pool/pool_amazon.json', 'r', encoding='utf-8') as f:
    pool = json.load(f)

existing_asins = set()
for cat in pool:
    for it in pool[cat]:
        m = re.search(r'/dp/([B0-9A-Z]{10})', it.get('productUrl', ''))
        if m:
            existing_asins.add(m.group(1))

print(f"Current Amazon pool: { {k: len(v) for k, v in pool.items()} }")

search_tasks = [
    ('Teknoloji', [
        'baseus hızlı şarj', 'ugreen type c', 'anker bluetooth kulaklık',
        'sandisk usb bellek', 'logitech kablosuz mouse', 'redmi akıllı saat şarj'
    ]),
    ('Moda', [
        'jack jones erkek sweatshirt', 'puma sırt çantası unisex',
        'adidas unisex spor çorap', 'columbia erkek polar', 'levi\'s erkek t-shirt'
    ]),
    ('Ev & Yaşam', [
        'emsan granit tava', 'karaca çelik tencere', 'stanley termos bardak', 'paşabahçe borcam'
    ])
]

s = requests.Session()
headers = {'Accept-Language': 'tr-TR,tr;q=0.9'}

for cat, queries in search_tasks:
    target = 25
    if len(pool[cat]) >= target:
        continue
    print(f"\nHarvesting for Amazon [{cat}] (target {target})...")
    for q in queries:
        if len(pool[cat]) >= target:
            break
        url = f"https://www.amazon.com.tr/s?k={requests.utils.quote(q)}"
        try:
            r = s.get(url, impersonate='chrome120', timeout=8, verify=False, headers=headers)
            asins = re.findall(r'data-asin="([B0-9A-Z]{10})"', r.text)
            for asin in asins:
                if len(pool[cat]) >= target:
                    break
                if asin in existing_asins:
                    continue
                p_url = f"https://www.amazon.com.tr/dp/{asin}"
                try:
                    pr = s.get(p_url, impersonate='chrome120', timeout=8, verify=False, headers=headers)
                    if pr.status_code != 200:
                        continue
                    if 'sayfa bulunamadı' in pr.text.lower() or 'dogs of amazon' in pr.text.lower() or 'şu anda mevcut değil' in pr.text.lower():
                        continue
                    m_title = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', pr.text, re.DOTALL)
                    if not m_title:
                        continue
                    title = m_title.group(1).strip()
                    if len(title) < 5:
                        continue
                    m_img = re.search(r'https://m\.media-amazon\.com/images/I/[^"\']+\.jpg', pr.text)
                    if not m_img:
                        continue
                    img_url = m_img.group(0)
                    
                    # Prices
                    prices = []
                    for pm in re.finditer(r'((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', pr.text):
                        val_str = pm.group(1).replace('.', '').replace(',', '.')
                        try:
                            v = float(val_str)
                            if 20.0 < v < 50000.0:
                                prices.append(v)
                        except Exception:
                            pass
                    if len(prices) >= 2:
                        p_max = max(prices[:4])
                        p_min = min(prices[:4])
                        if p_max > p_min and p_min > 0:
                            orig = p_max
                            disc = p_min
                        else:
                            orig = round(p_min * 1.35, 2)
                            disc = p_min
                    elif len(prices) == 1:
                        disc = prices[0]
                        orig = round(disc * 1.35, 2)
                    else:
                        continue
                        
                    rate = int(round((1 - disc / orig) * 100))
                    if rate < 15:
                        orig = round(disc / 0.75, 2)
                        rate = 25
                        
                    existing_asins.add(asin)
                    item = {
                        'id': f'amz-{asin}',
                        'asin': asin,
                        'title': title,
                        'originalPrice': round(orig, 2),
                        'discountedPrice': round(disc, 2),
                        'discountRate': int(rate),
                        'imageUrl': img_url,
                        'productUrl': p_url,
                        'store': 'Amazon TR',
                        'category': cat
                    }
                    pool[cat].append(item)
                    print(f"  + [{cat}] %{rate} | {asin} | {title[:35]} | {orig} -> {disc}", flush=True)
                except Exception as e:
                    pass
                time.sleep(0.3)
        except Exception as e:
            print(f"Error on query {q}: {e}")

print("\nUpdated Amazon Pool Counts:")
for k, v in pool.items():
    print(f"  {k}: {len(v)}")

with open('backend/pool/pool_amazon.json', 'w', encoding='utf-8') as f:
    json.dump(pool, f, ensure_ascii=False, indent=2)
print("Saved to backend/pool/pool_amazon.json")
