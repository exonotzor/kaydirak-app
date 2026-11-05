import requests
import urllib3
import json
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

with open('scraper/idefix_all_categories.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

print(f"Loaded {len(categories)} categories.")

def categorize(name, url):
    u = url.lower()
    n = name.lower()
    
    # Moda
    if any(k in u for k in ['ayakkabi', 'canta', 'valiz', 'giyim', 'saat', 'gozluk', 'taki', 'aksesuar', 'terlik', 'bot', 'sneaker', 'mont', 'ceket']) or \
       any(k in n for k in ['ayakkabı', 'çanta', 'valiz', 'giyim', 'polo', 'elbise', 'pantolon', 'tişört', 'gömlek', 'ceket', 'mont', 'bot', 'sneaker', 'deri']):
        return 'Moda'
        
    # Kozmetik
    if any(k in u for k in ['kozmetik', 'parfum', 'cilt', 'makyaj', 'sac', 'kisisel', 'deodorant', 'krem', 'serum', 'gunes', 'losyon']) or \
       any(k in n for k in ['parfüm', 'deodorant', 'ruj', 'maskara', 'fondöten', 'krem', 'serum', 'şampuan', 'cilt', 'makyaj', 'losyon', 'kolonya', 'göz']):
        return 'Kozmetik'
        
    # Teknoloji
    if any(k in u for k in ['elektronik', 'telefon', 'gaming', 'kulaklik', 'bilgisayar', 'tablet', 'oyuncu', 'mouse', 'klavye', 'konsol', 'tv', 'kamera', 'ses', 'sarj', 'kablo', 'giyilebilir', 'saatler']) or \
       any(k in n for k in ['telefon', 'kulaklık', 'mouse', 'klavye', 'kablo', 'şarj', 'adaptör', 'bluetooth', 'powerbank', 'hoparlör', 'kılıf', 'gaming', 'oyuncu', 'akıllı saat', 'usb']):
        return 'Teknoloji'
        
    # Ev & Yaşam
    if any(k in u for k in ['ev-', 'mutfak', 'sofra', 'tekstil', 'banyo', 'aydinlatma', 'mobilya', 'dekorasyon', 'yasam', 'temizlik', 'deterjan', 'gerecleri', 'aletleri']) or \
       any(k in n for k in ['tencere', 'tava', 'bıçak', 'nevresim', 'yastık', 'yorgan', 'havlu', 'bardak', 'fincan', 'tabak', 'termos', 'lamba', 'avize', 'halı', 'perde', 'süpürge', 'ütü', 'blender', 'tost']):
        return 'Ev & Yaşam'

    return None

def fetch_category_page(cat_info, page=1):
    url = f"https://www.idefix.com{cat_info['url']}?sayfa={page}"
    deals = []
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=8)
        if '__NEXT_DATA__' not in r.text:
            return deals
        soup = BeautifulSoup(r.text, 'html.parser')
        s = soup.find('script', id='__NEXT_DATA__')
        if not s or not s.string:
            return deals
        d = json.loads(s.string)
        pp = d.get('props', {}).get('pageProps', {})
        items = pp.get('categoryData', {}).get('items', [])
        
        for it in items:
            for v in it.get('variants', []):
                vid = str(v.get('id') or '')
                name = (v.get('name') or '').strip()
                if not name or not vid:
                    continue
                price = float(v.get('price') or 0)
                disc_price = float(v.get('discountedSalesPrice') or price)
                if price <= 0 or disc_price <= 0 or disc_price >= price:
                    continue
                rate = round(((price - disc_price) / price) * 100)
                if rate < 50:
                    continue
                    
                imgs = v.get('images', [])
                if not imgs:
                    continue
                img_src = imgs[0].get('src', '').replace('{size}', '600/600/')
                if not img_src.startswith('http'):
                    continue
                    
                slug = v.get('handleUrl') or ''
                if not slug:
                    continue
                product_url = f"https://www.idefix.com{slug}"
                
                cat = categorize(name, cat_info['url'])
                if not cat:
                    continue
                    
                deals.append({
                    'id': f'idefix-{vid}',
                    'title': name,
                    'originalPrice': price,
                    'discountedPrice': disc_price,
                    'discountRate': rate,
                    'imageUrl': img_src,
                    'productUrl': product_url,
                    'store': 'Idefix',
                    'category': cat,
                })
    except Exception:
        pass
    return deals

tasks = []
# Select diverse categories across the 4 domains
for cat_info in categories:
    cat = categorize(cat_info['name'], cat_info['url'])
    if cat:
        for p in range(1, 4):  # Check pages 1, 2, 3
            tasks.append((cat_info, p))

print(f"Total tasks to execute: {len(tasks)}")

all_deals = {}
with ThreadPoolExecutor(max_workers=12) as executor:
    futures = {executor.submit(fetch_category_page, cat_info, p): (cat_info, p) for cat_info, p in tasks}
    count = 0
    for f in as_completed(futures):
        count += 1
        res = f.result()
        for d in res:
            if d['id'] not in all_deals:
                all_deals[d['id']] = d
        if count % 50 == 0 or count == len(tasks):
            print(f"Progress: {count}/{len(tasks)} tasks finished. Unique deals found: {len(all_deals)}")

deals_list = list(all_deals.values())
cat_counts = {}
for d in deals_list:
    cat_counts[d['category']] = cat_counts.get(d['category'], 0) + 1

print("\n=== HARVEST SUMMARY ===")
print(f"Total deals: {len(deals_list)}")
for c, cnt in cat_counts.items():
    print(f"  {c:15}: {cnt}")

with open('scraper/harvested_deals_raw.json', 'w', encoding='utf-8') as f:
    json.dump(deals_list, f, ensure_ascii=False, indent=2)

print("Saved to scraper/harvested_deals_raw.json")
