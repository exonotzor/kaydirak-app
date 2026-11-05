import requests
import urllib3
import json
import re
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0'}

urls = [
    ('Sofra, Mutfak', '/sofra-mutfak-c-2206'),
    ('Ev Dekorasyon', '/ev-dekorasyon-c-2202'),
    ('Aydınlatma', '/aydinlatma-c-2201'),
    ('Deterjan ve Temizlik Ürünleri', '/ev-temizlik-c-8802'),
]

tasks = []
for name, u in urls:
    for p in range(1, 41):
        tasks.append((name, u, p))

def scan_page(task):
    cat_name, u, p = task
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
                    if 45 <= rate <= 80:
                        img_url = imgs[0].get('src', '').replace('{size}', '600/600/')
                        found.append({
                            'id': f"idefix-{v.get('id')}",
                            'title': name,
                            'category': 'Ev & Yaşam',
                            'subCategory': cat_name,
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
            
    print(f"Total raw found: {len(all_found)}")
    unique = {d['id']: d for d in all_found}
    print(f"Unique strictly verified Ev & Yaşam deals (>= 45%): {len(unique)}")
    with open('scraper/top_home_strict.json', 'w', encoding='utf-8') as f:
        json.dump(list(unique.values()), f, ensure_ascii=False, indent=2)
    print("Saved to scraper/top_home_strict.json")
