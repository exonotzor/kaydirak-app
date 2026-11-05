import requests
import urllib3
import json
import re
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0'}

extra_urls = [
    '/yapi-market-bahce-c-53',
    '/bahce-dekorasyon-c-5301252590',
    '/bahce-aydinlatma-c-5301714910',
    '/pet-shop-c-66',
    '/evcil-hayvan-urunleri-c-6610',
    '/kirtasiye-c-3305',
    '/ofis-mobilyasi-c-2205933040',
    '/bebek-oyuncaklari-c-1106118900',
    '/yapi-market-c-5303',
    '/bahce-c-5301',
]

tasks = []
for u in extra_urls:
    for p in range(1, 15):
        tasks.append((u, p))

def scan_page(task):
    u, p = task
    url = f"https://www.idefix.com{u}?sayfa={p}"
    found = []
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=4)
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text)
        if m:
            d = json.loads(m.group(1))
            items = d.get('props',{}).get('pageProps',{}).get('categoryData',{}).get('items',[])
            for it in items:
                for v in it.get('variants', []):
                    p_orig = float(v.get('price') or 0)
                    p_disc = float(v.get('discountedSalesPrice') or p_orig)
                    name = (v.get('name') or '').strip()
                    handle = v.get('handleUrl') or ''
                    imgs = v.get('images', [])
                    if not name or not handle or not imgs or p_orig <= 0 or p_disc <= 0:
                        continue
                    if p_disc >= p_orig:
                        continue
                    rate = round(((p_orig - p_disc) / p_orig) * 100)
                    if 50 <= rate <= 80:
                        img_url = imgs[0].get('src', '').replace('{size}', '600/600/')
                        found.append({
                            'id': f"idefix-{v.get('id')}",
                            'title': name,
                            'category': 'Ev & Yaşam',
                            'store': 'Idefix',
                            'originalPrice': p_orig,
                            'discountedPrice': p_disc,
                            'discountRate': rate,
                            'productUrl': f"https://www.idefix.com/{handle}",
                            'imageUrl': img_url,
                        })
    except Exception:
        pass
    return found

if __name__ == '__main__':
    all_found = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        for res in ex.map(scan_page, tasks):
            all_found.extend(res)
            
    print(f"Extra home deals found: {len(all_found)}")
    unique = {d['id']: d for d in all_found}
    print(f"Unique extra deals: {len(unique)}")
    with open('scraper/extra_home_strict.json', 'w', encoding='utf-8') as f:
        json.dump(list(unique.values()), f, ensure_ascii=False, indent=2)
    for x in list(unique.values())[:10]:
        print(f"  %{x['discountRate']} | {x['discountedPrice']} TL (was {x['originalPrice']} TL) | {x['title'][:40]}")
