import json
import requests
import urllib3
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

with open('scraper/idefix_all_categories.json', 'r', encoding='utf-8') as f:
    all_cats = json.load(f)

def categorize(cat_name, cat_url):
    u = cat_url.lower()
    n = cat_name.lower()
    
    # Moda
    if any(k in u for k in ['ayakkabi', 'canta', 'valiz', 'giyim', 'saat', 'gozluk', 'taki', 'aksesuar', 'terlik', 'bot', 'sneaker', 'mont', 'ceket', 'kadin', 'erkek', 'cocuk', 'elbise', 'polo', 'gomlek', 'pantolon']) or \
       any(k in n for k in ['ayakkabı', 'çanta', 'valiz', 'giyim', 'saat', 'gözlük', 'takı', 'elbise', 'gömlek', 'pantolon', 'mont']):
        return 'Moda'
        
    # Kozmetik
    if any(k in u for k in ['kozmetik', 'parfum', 'cilt', 'makyaj', 'sac', 'kisisel', 'saglik', 'deodorant', 'krem', 'serum', 'losyon', 'roll-on']) or \
       any(k in n for k in ['kozmetik', 'parfüm', 'cilt', 'makyaj', 'saç', 'kişisel', 'bakım', 'krem', 'deodorant']):
        return 'Kozmetik'
        
    # Ev & Yaşam
    if any(k in u for k in ['ev-', 'mutfak', 'sofra', 'tekstil', 'banyo', 'aydinlatma', 'mobilya', 'dekorasyon', 'yasam', 'temizlik', 'gerecleri', 'aletleri', 'yapi-market', 'evcil', 'tencere', 'tava', 'bicak', 'bardak', 'fincan', 'deterjan']) or \
       any(k in n for k in ['ev ', 'mutfak', 'sofra', 'tekstil', 'banyo', 'aydınlatma', 'mobilya', 'dekorasyon', 'temizlik', 'deterjan']):
        return 'Ev & Yaşam'

    # Teknoloji
    if any(k in u for k in ['elektronik', 'teknoloji', 'telefon', 'gaming', 'kulaklik', 'bilgisayar', 'tablet', 'oyuncu', 'mouse', 'klavye', 'sarj', 'kablo', 'giyilebilir', 'tv', 'ses', 'kamera', 'hoparlor', 'powerbank']) or \
       any(k in n for k in ['telefon', 'kulaklık', 'mouse', 'klavye', 'şarj', 'kablo', 'bluetooth', 'hoparlör', 'gaming', 'elektronik', 'bilgisayar']):
        return 'Teknoloji'

    return None

tasks = []
for c in all_cats:
    cat = categorize(c['name'], c['url'])
    if cat:
        for p in range(1, 5): # check first 4 pages of each category
            tasks.append((cat, c['url'], p))

print(f"Total category-page tasks to scan: {len(tasks)}")

def scan_task(task):
    cat, url_path, page = task
    full_url = f"https://www.idefix.com{url_path}?sayfa={page}"
    found = []
    try:
        r = requests.get(full_url, headers=headers, verify=False, timeout=6)
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
                name = (v.get('name') or '').strip()
                handle = v.get('handleUrl') or ''
                imgs = v.get('images', [])
                if not name or not handle or not imgs or p_orig <= 0 or p_disc <= 0:
                    continue
                if p_disc >= p_orig:
                    continue
                rate = round(((p_orig - p_disc) / p_orig) * 100)
                # STRICT ON-PAGE RULE: Must be >= 50% and <= 80% (reasonable, real visible discount)
                if 50 <= rate <= 80:
                    img_url = imgs[0].get('src', '').replace('{size}', '600/600/')
                    prod_url = f"https://www.idefix.com/{handle}"
                    found.append({
                        'id': f"idefix-{v.get('id')}",
                        'title': name,
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

print("Scanning Idefix categories with 15 parallel threads...")
all_found = []
with ThreadPoolExecutor(max_workers=15) as ex:
    results = ex.map(scan_task, tasks)
    for res in results:
        all_found.extend(res)

print(f"\nScan completed! Found {len(all_found)} raw deals meeting >= 50% on-page discount.")

# Deduplicate by id
unique_deals = {}
for d in all_found:
    unique_deals[d['id']] = d

print(f"Unique verified Idefix deals: {len(unique_deals)}")
from collections import Counter
counts = Counter(d['category'] for d in unique_deals.values())
for cat, cnt in counts.items():
    print(f"  {cat:15}: {cnt} deals")

with open('scraper/idefix_strict_onpage.json', 'w', encoding='utf-8') as f:
    json.dump(list(unique_deals.values()), f, ensure_ascii=False, indent=2)
print("Saved to scraper/idefix_strict_onpage.json")
