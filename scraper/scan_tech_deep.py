import requests
import urllib3
import json
import re
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

tech_urls = [
    '/cep-telefonu-aksesuarlari-c-2313374140',
    '/teknoloji-aksesuarlari-l-107820',
    '/konsol-aksesuarlari-c-2308758120',
    '/gaming-kulaklik-c-230890672',
    '/pc-joystick-gamepad-aksesuarlari-c-230865728',
    '/yayinci-aksesuarlari-c-230898265',
    '/gaming-mouse-c-230861751',
    '/gaming-mousepad-c-230811748',
    '/gaming-klavye-c-230835467',
    '/outlet-bilgisayar-ve-tablet-c-2317130060',
    '/giyilebilir-teknoloji-c-2309',
    '/akilli-saatler-smartwatch-c-230993929',
    '/tv-goruntu-ses-c-2314',
    '/sarjli-supurgeler-c-2311462460',
    '/supurge-aksesuarlari-c-2311565890',
    '/bilgisayar-ve-tablet-c-2302',
    '/gaming-oyuncu-c-2308',
]

tasks = []
for u in tech_urls:
    for p in range(1, 11):
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
                    if p_orig > 0 and 0 < p_disc < p_orig:
                        rate = round(((p_orig - p_disc) / p_orig) * 100)
                        img = (v.get('images', [{}])[0].get('src') or '').replace('{size}', '600/600/')
                        found.append({
                            'id': f"idefix-{v.get('id')}",
                            'rate': rate,
                            'title': (v.get('name') or '').strip(),
                            'originalPrice': p_orig,
                            'discountedPrice': p_disc,
                            'cat_url': u,
                            'handle': v.get('handleUrl'),
                            'imageUrl': img
                        })
    except Exception:
        pass
    return found

print(f"Scanning {len(tasks)} tech category pages...", flush=True)
all_items = []
with ThreadPoolExecutor(max_workers=20) as ex:
    for res in ex.map(scan_page, tasks):
        all_items.extend(res)

print(f"Total discounted items found: {len(all_items)}", flush=True)
all_items.sort(key=lambda x: x['rate'], reverse=True)
for d in all_items[:40]:
    print(f"%{d['rate']} | {d['discountedPrice']} TL (was {d['originalPrice']} TL) | {d['title'][:40]} | URL: {d['handle']}", flush=True)

with open('scraper/tech_scanned.json', 'w', encoding='utf-8') as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)
print("Saved to scraper/tech_scanned.json", flush=True)
