import requests
import urllib3
import json
import re
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

with open('scraper/idefix_all_categories.json', 'r', encoding='utf-8') as f:
    all_cats = json.load(f)

# Find top Ev & Yaşam and Kozmetik categories
home_cats = []
beauty_cats = []

for c in all_cats:
    u = c['url'].lower()
    n = c['name'].lower()
    if any(k in u or k in n for k in ['kozmetik', 'parfum', 'parfüm', 'cilt', 'makyaj', 'kisisel', 'kişisel', 'bakim', 'bakım', 'serum', 'krem', 'deodorant']):
        beauty_cats.append(c)
    elif any(k in u or k in n for k in ['ev-', 'mutfak', 'sofra', 'tekstil', 'banyo', 'aydinlatma', 'mobilya', 'dekorasyon', 'yasam', 'yaşam', 'temizlik', 'deterjan', 'tencere', 'tava', 'bicak', 'bardak', 'yatak']):
        home_cats.append(c)

print(f"Target categories: Beauty: {len(beauty_cats)}, Home: {len(home_cats)}")

tasks = []
# For each category, scan pages 1 to 15
for c in beauty_cats:
    for p in range(1, 16):
        tasks.append(('Kozmetik', c['url'], p))

for c in home_cats:
    for p in range(1, 16):
        tasks.append(('Ev & Yaşam', c['url'], p))

print(f"Total tasks to scan: {len(tasks)}")

def scan_task(task):
    cat, u, p = task
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
                            'category': cat,
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
        for res in ex.map(scan_task, tasks):
            all_found.extend(res)
            
    print(f"Raw deals found: {len(all_found)}")
    unique = {d['id']: d for d in all_found}
    print(f"Unique deals: {len(unique)}")
    from collections import Counter
    counts = Counter(d['category'] for d in unique.values())
    for cat, cnt in counts.items():
        print(f"  {cat}: {cnt} deals")
        
    with open('scraper/home_beauty_strict.json', 'w', encoding='utf-8') as f:
        json.dump(list(unique.values()), f, ensure_ascii=False, indent=2)
    print("Saved to scraper/home_beauty_strict.json")
