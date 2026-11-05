import json
import requests
import urllib3
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0'}

with open('scraper/idefix_all_categories.json', 'r', encoding='utf-8') as f:
    all_cats = json.load(f)

# Select non-Moda categories (Teknoloji, Ev & Yaşam, Kozmetik)
target_cats = []
for c in all_cats:
    u = c['url'].lower()
    n = c['name'].lower()
    cat = None
    if any(k in u for k in ['elektronik', 'teknoloji', 'telefon', 'gaming', 'kulaklik', 'bilgisayar', 'tablet', 'oyuncu', 'mouse', 'klavye', 'sarj', 'kablo', 'giyilebilir', 'tv', 'ses', 'kamera']):
        cat = 'Teknoloji'
    elif any(k in u for k in ['kozmetik', 'parfum', 'cilt', 'makyaj', 'sac', 'kisisel', 'saglik', 'deodorant']):
        cat = 'Kozmetik'
    elif any(k in u for k in ['ev-', 'mutfak', 'sofra', 'tekstil', 'banyo', 'aydinlatma', 'mobilya', 'dekorasyon', 'yasam', 'temizlik', 'gerecleri', 'aletleri']):
        cat = 'Ev & Yaşam'
        
    if cat:
        # scan pages 1 to 8
        for p in range(1, 9):
            target_cats.append((cat, c['name'], c['url'], p))

print(f"Total target page tasks: {len(target_cats)}")

def scan_task(task):
    cat, name, url_path, page = task
    url = f"https://www.idefix.com{url_path}?sayfa={page}"
    found = []
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=5)
        if '__NEXT_DATA__' not in r.text:
            return found
        soup = BeautifulSoup(r.text, 'html.parser')
        s = soup.find('script', id='__NEXT_DATA__')
        if not s or not s.string:
            return found
        d = json.loads(s.string)
        items = d.get('props', {}).get('pageProps', {}).get('categoryData', {}).get('items', [])
        for it in items:
            for v in it.get('variants', []):
                p_orig = float(v.get('price') or 0)
                p_disc = float(v.get('discountedSalesPrice') or p_orig)
                name_prod = (v.get('name') or '').strip()
                handle = v.get('handleUrl') or ''
                imgs = v.get('images', [])
                if not name_prod or not handle or not imgs or p_orig <= 0 or p_disc <= 0:
                    continue
                if p_disc >= p_orig:
                    continue
                rate = round(((p_orig - p_disc) / p_orig) * 100)
                if 50 <= rate <= 80:
                    img_url = imgs[0].get('src', '').replace('{size}', '600/600/')
                    prod_url = f"https://www.idefix.com/{handle}"
                    found.append({
                        'id': f"idefix-{v.get('id')}",
                        'title': name_prod,
                        'category': cat,
                        'store': 'Idefix',
                        'originalPrice': p_orig,
                        'discountedPrice': p_disc,
                        'discountRate': rate,
                        'productUrl': prod_url,
                        'imageUrl': img_url,
                    })
    except Exception:
        pass
    return found

with ThreadPoolExecutor(max_workers=20) as ex:
    results = ex.map(scan_task, target_cats)
    all_deals = []
    for r in results:
        all_deals.extend(r)

print(f"Found {len(all_deals)} raw deals.")
unique = {d['id']: d for d in all_deals}
print(f"Unique deals: {len(unique)}")
from collections import Counter
print(Counter(d['category'] for d in unique.values()))
