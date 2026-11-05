import requests
import urllib3
import json
import re
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

with open('scraper/idefix_all_categories.json', 'r', encoding='utf-8') as f:
    all_cats = json.load(f)

# Select all categories that can qualify as Teknoloji
tech_cats = []
for c in all_cats:
    u = c['url'].lower()
    n = c['name'].lower()
    if any(k in u or k in n for k in [
        'elektronik', 'teknoloji', 'telefon', 'bilgisayar', 'tablet', 
        'kulaklik', 'kulaklık', 'sarj', 'şarj', 'kablo', 'powerbank', 
        'gaming', 'oyuncu', 'hoparlor', 'hoparlör', 'kamera', 'foto', 
        'saat', 'akilli', 'akıllı', 'aksesuar', 'tv', 'ses', 'goruntu', 
        'görüntü', 'konsol', 'joystick', 'mouse', 'klavye', 'hafiza', 
        'hafıza', 'usb', 'modem', 'router', 'donanim', 'donanım', 'cevre', 'çevre'
    ]):
        if not any(k in u for k in ['kadin', 'erkek-giyim', 'taki', 'canta', 'ayakkabi', 'bebek', 'mama', 'oto-koltugu']):
            tech_cats.append(c)

print(f"Selected {len(tech_cats)} potential tech categories.")

# Generate tasks for pages 1 to 10
tasks = []
for c in tech_cats:
    for p in range(1, 11):
        tasks.append((c['name'], c['url'], p))

print(f"Total tech scan tasks: {len(tasks)}")

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
                    # We want to see all real discounts
                    if rate >= 10:
                        img_url = imgs[0].get('src', '').replace('{size}', '600/600/')
                        found.append({
                            'id': f"idefix-{v.get('id')}",
                            'title': name,
                            'category': 'Teknoloji',
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
            
    print(f"Total discounted tech items found: {len(all_found)}")
    unique = {d['id']: d for d in all_found}
    unique_list = list(unique.values())
    unique_list.sort(key=lambda x: x['discountRate'], reverse=True)
    print(f"Unique tech items with discount >= 10%: {len(unique_list)}")
    
    with open('scraper/all_tech_verified.json', 'w', encoding='utf-8') as f:
        json.dump(unique_list, f, ensure_ascii=False, indent=2)
    print("Saved to scraper/all_tech_verified.json")
    
    for x in unique_list[:20]:
        print(f"  %{x['discountRate']} | {x['discountedPrice']} TL (was {x['originalPrice']} TL) | {x['title'][:40]} | Sub: {x['subCategory']}")
