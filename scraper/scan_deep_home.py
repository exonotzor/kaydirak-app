import requests
import urllib3
import json
import re
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0'}

urls = [
    '/sofra-mutfak-c-2207',
    '/ev-tekstili-c-2203',
    '/banyo-tekstili-c-22031123',
    '/yatak-odasi-tekstili-c-22031124',
    '/pisirme-urunleri-c-22071111',
    '/tencereler-ve-tavalar-c-2207111110',
    '/sofra-ve-servis-urunleri-c-22071112',
    '/mutfak-gerecleri-c-22071113',
    '/ev-duzeni-ve-temizlik-c-2204',
    '/deterjan-ve-temizlik-urunleri-c-22041126',
]

tasks = []
for u in urls:
    for p in range(1, 25):
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
                    # We accept >= 45% (which is essentially half price)
                    if 45 <= rate <= 80:
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
    with ThreadPoolExecutor(max_workers=25) as ex:
        for res in ex.map(scan_page, tasks):
            all_found.extend(res)
            
    print(f"Total raw found: {len(all_found)}")
    unique = {d['id']: d for d in all_found}
    print(f"Unique home deals (>= 45%): {len(unique)}")
    with open('scraper/deep_home_deals.json', 'w', encoding='utf-8') as f:
        json.dump(list(unique.values()), f, ensure_ascii=False, indent=2)
    print("Saved to scraper/deep_home_deals.json")
