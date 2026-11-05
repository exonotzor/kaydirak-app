import requests
import json
import re
import urllib3
import time
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

urllib3.disable_warnings()

headers = {'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)'}

queries = {
    'Teknoloji': [
        'bluetooth kulaklık', 'kablosuz mouse', 'mekanik klavye', 'powerbank 20000',
        'akıllı saat', 'bluetooth hoparlör', 'hızlı şarj aleti', 'taşınabilir ssd',
        'gaming kulaklık', 'usb bellek 128gb', 'akıllı bileklik', 'oyuncu kulaklığı',
        'type c kablo', 'şarj adaptörü', 'tablet kılıfı'
    ],
    'Moda': [
        'erkek mont', 'kadın mont', 'erkek sweatshirt', 'kadın hırka',
        'erkek spor ayakkabı', 'kadın ceket', 'erkek eşofman altı', 'kadın çanta',
        'erkek gömlek slim fit', 'kadın trençkot', 'unisex sırt çantası', 'erkek polar',
        'kadın kazak boğazlı', 'erkek deri kemer', 'unisex bere'
    ],
    'Kozmetik': [
        'parfüm edp', 'güneş kremi spf 50', 'c vitamini serum', 'yüz nemlendirici krem',
        'şampuan keratin', 'vücut spreyi', 'göz çevresi kremi', 'hyaluronik asit serum',
        'kolajen serum', 'yüz temizleme jeli', 'arganyağı saç', 'nivea krem',
        'el ve vücut kremi', 'dudak nemlendirici', 'micellar su'
    ],
    'Ev & Yaşam': [
        'döküm tava', 'granit tencere seti', 'bıçak seti şef', 'kahve fincan takımı',
        'çelik termos', 'borcam fırın tepsisi', 'pamuk nevresim takımı', 'banyo havlusu set',
        'vakumlu saklama kabı', 'baharatlık takımı', 'çay bardağı seti', 'çift kişilik pike',
        'kesme tahtası bambu', 'su ısıtıcı kettle', 'kupa bardak takımı'
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

# Load existing Hepsiburada pool if present
pool = {'Teknoloji': [], 'Moda': [], 'Kozmetik': [], 'Ev & Yaşam': []}
try:
    with open('backend/pool/pool_hepsiburada.json', 'r', encoding='utf-8') as f:
        pool = json.load(f)
except Exception:
    pass

seen_urls = set(it['productUrl'] for cat_items in pool.values() for it in cat_items)
seen_titles = set(it['title'].lower() for cat_items in pool.values() for it in cat_items)

print(f"Starting Hepsiburada harvesting. Current counts: { {k: len(v) for k, v in pool.items()} }")

for cat, q_list in queries.items():
    print(f"\nHarvesting {cat}...")
    for q in q_list:
        if len(pool[cat]) >= 50:
            print(f"  Reached 50+ items for {cat}, moving to next.")
            break
        url = f"https://www.hepsiburada.com/ara?q={requests.utils.quote(q)}"
        try:
            r = requests.get(url, headers=headers, verify=False, timeout=8)
            if r.status_code != 200:
                continue
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
                        if title.lower() in seen_titles:
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
                        seen_titles.add(title.lower())
                        item_id = f"hb-{p.get('productId') or str(abs(hash(title)))[:10]}"
                        item = {
                            'id': item_id,
                            'title': title,
                            'originalPrice': round(orig_p, 2),
                            'discountedPrice': round(sale_p, 2),
                            'discountRate': int(rate),
                            'imageUrl': img_url,
                            'productUrl': prod_url,
                            'store': 'Hepsiburada',
                            'category': cat
                        }
                        pool[cat].append(item)
                        print(f"  + [{cat}] %{rate} | {title[:40]} | {orig_p:.1f} -> {sale_p:.1f}")
                        if len(pool[cat]) >= 50:
                            break
                    break
            time.sleep(0.3)
        except Exception as e:
            print(f"Error on {q}: {e}")

print("\nFinal Hepsiburada pool sizes:")
for c in pool:
    print(f"  {c}: {len(pool[c])}")

with open('backend/pool/pool_hepsiburada.json', 'w', encoding='utf-8') as f:
    json.dump(pool, f, ensure_ascii=False, indent=2)
print("Saved to backend/pool/pool_hepsiburada.json")
