import requests
import re
import json
import urllib3
import time
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

urllib3.disable_warnings()

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    prev_deals = json.load(f)
prev_titles = set(d['title'].strip().lower() for d in prev_deals)

headers = {'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)'}

cat_queries = {
    'Teknoloji': [
        'bluetooth kulaklik', 'oyuncu mouse', 'mekanik klavye', 'powerbank',
        'akilli saat', 'bluetooth hoparlor', 'sarj aleti', 'tasinabilir ssd',
        'gaming kulaklik', 'usb bellek', 'laptop sogutucu', 'webcam'
    ],
    'Moda': [
        'erkek mont', 'kadin mont', 'erkek sweatshirt', 'kadin hirka',
        'erkek ayakkabi', 'kadin ceket', 'esofman alti', 'kadin canta',
        'erkek kazak', 'kadin trenckot', 'unisex sirt cantasi'
    ],
    'Kozmetik': [
        'parfum edp', 'gunes kremi spf 50', 'c vitamini serum', 'yuz nemlendirici',
        'sampuan keratin', 'vucut spreyi', 'goz kremi', 'hyaluronik asit serum',
        'sac maskesi', 'ruj mat', 'el kremi', 'tonik'
    ],
    'Ev & Yaşam': [
        'dokum tava', 'granit tencere', 'bicak seti', 'kahve fincani',
        'termos paslanmaz', 'borcam', 'nevresim takimi', 'banyo havlusu',
        'saklama kabi', 'baharatlik', 'cay bardagi seti'
    ]
}

banned_in_tech = [
    'parka', 'kaban', 'ceket', 'mont', 'yelek', 'şort', 'sort', 'kapri', 'pantolon',
    't-shirt', 'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı', 'bot',
    'çorap', 'gömlek', 'polar', 'tayt', 'içlik', 'boxer', 'atlet', 'elbise', 'etek',
    'buzluk', 'cooler', 'stein', 'bardak', 'termos', 'matara', 'tava', 'tencere', 'krampon',
    'çanta', 'canta', 'tozluk', 'eldiven', 'bere', 'şapka', 'sapka', 'bikini', 'mayo',
    'krem', 'serum', 'losyon', 'deodorant', 'parfüm', 'sabun'
]

hb_fresh = {c: [] for c in cat_queries}
seen_urls = set(d['productUrl'] for d in prev_deals)

for cat, queries in cat_queries.items():
    print(f"Harvesting for HB category: {cat}...", flush=True)
    for q in queries:
        if len(hb_fresh[cat]) >= 16:
            break
        url = f"https://www.hepsiburada.com/ara?q={requests.utils.quote(q)}"
        try:
            r = requests.get(url, headers=headers, verify=False, timeout=8)
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)
            for s in scripts:
                s_clean = s.strip()
                if s_clean.startswith('{') and 'productStat' in s_clean:
                    data = json.loads(s_clean)
                    prods = data.get('searchState', {}).get('searchProductArray', [])
                    for p in prods:
                        title = p.get('name', '').strip()
                        if not title or len(title) < 5:
                            continue
                        if title.lower() in prev_titles:
                            continue
                        
                        prod_url = p.get('productUrl', '')
                        if not prod_url:
                            continue
                        if not prod_url.startswith('http'):
                            prod_url = 'https://www.hepsiburada.com' + prod_url
                        if prod_url in seen_urls:
                            continue
                        
                        if cat == 'Teknoloji':
                            tl = title.lower()
                            if any(w in tl for w in banned_in_tech):
                                continue
                                
                        pa = p.get('priceArea', {}).get('priceInfo', {})
                        tp = pa.get('topPrice')
                        bp = pa.get('bottomPrice')
                        if not tp or not bp:
                            continue
                        
                        orig_p = float(tp.get('value', 0))
                        sale_p = float(bp.get('value', 0))
                        if sale_p <= 0 or orig_p <= sale_p:
                            continue
                        
                        rate = round(((orig_p - sale_p) / orig_p) * 100)
                        if rate < 15 or rate > 80:
                            continue
                        
                        imgs = p.get('images', [])
                        if not imgs:
                            continue
                        img_url = imgs[0].get('linkFormat', '').replace('{size}', '550')
                        if not img_url:
                            continue
                        
                        seen_urls.add(prod_url)
                        prev_titles.add(title.lower())
                        item_id = f"hb-{p.get('productId') or str(abs(hash(title)))[:10]}"
                        item = {
                            'id': item_id,
                            'title': title,
                            'originalPrice': orig_p,
                            'discountedPrice': sale_p,
                            'discountRate': rate,
                            'imageUrl': img_url,
                            'productUrl': prod_url,
                            'store': 'Hepsiburada',
                            'category': cat
                        }
                        hb_fresh[cat].append(item)
                        print(f"  [{cat}] %{rate} | {title[:45]} | {orig_p:.2f} -> {sale_p:.2f}", flush=True)
                        if len(hb_fresh[cat]) >= 16:
                            break
                    break
            time.sleep(0.4)
        except Exception as e:
            print(f"Error fetching {q}: {e}", flush=True)

for c, items in hb_fresh.items():
    print(f"Total fresh HB for {c}: {len(items)}", flush=True)

with open('scraper/hb_harvested_fresh.json', 'w', encoding='utf-8') as f:
    json.dump(hb_fresh, f, ensure_ascii=False, indent=2)
print("Saved to scraper/hb_harvested_fresh.json", flush=True)
