import requests
import urllib3
import json
import re
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

with open('scraper/idefix_all_categories.json', 'r', encoding='utf-8') as f:
    all_cats = json.load(f)

home_cats = []
for c in all_cats:
    u = c['url'].lower()
    n = c['name'].lower()
    if any(k in u or k in n for k in [
        'ev-', 'mutfak', 'sofra', 'tekstil', 'banyo', 'aydinlatma', 
        'mobilya', 'dekorasyon', 'yasam', 'yaşam', 'temizlik', 'deterjan', 
        'tencere', 'tava', 'bicak', 'bardak', 'yatak', 'hali', 'halı', 
        'perde', 'nevresim', 'pike', 'havlu', 'yorgan', 'yastik', 'yastık',
        'duzenleyici', 'saklama', 'kavanoz', 'tabak', 'kupa', 'fincan', 'termos'
    ]):
        home_cats.append(c)

print(f"Total home categories: {len(home_cats)}")

tasks = []
for c in home_cats:
    for p in range(1, 20):
        tasks.append((c['name'], c['url'], p))

print(f"Total home tasks: {len(tasks)}")

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
                    if 50 <= rate <= 80:
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
    with ThreadPoolExecutor(max_workers=25) as ex:
        for res in ex.map(scan_page, tasks):
            all_found.extend(res)
            
    print(f"Total raw home deals: {len(all_found)}")
    unique = {d['id']: d for d in all_found}
    print(f"Unique strictly verified Ev & Yaşam deals (>= 50%): {len(unique)}")
    with open('scraper/all_home_strict.json', 'w', encoding='utf-8') as f:
        json.dump(list(unique.values()), f, ensure_ascii=False, indent=2)
    print("Saved to scraper/all_home_strict.json")
