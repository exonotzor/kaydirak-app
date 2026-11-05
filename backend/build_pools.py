import json
import glob
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

CATEGORIES = ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']

def clean_item(item, default_store, default_cat=None):
    if not isinstance(item, dict):
        return None
    title = str(item.get('title') or item.get('name') or '').strip()
    url = str(item.get('productUrl') or item.get('url') or item.get('link') or '').strip()
    img = str(item.get('imageUrl') or item.get('image') or '').strip()
    cat = item.get('category') or default_cat or ''
    if cat not in CATEGORIES:
        # Category normalization
        tl = title.lower()
        if any(w in tl for w in ['saat', 'kulaklık', 'şarj', 'kablo', 'powerbank', 'mouse', 'klavye', 'hoparlör', 'pil', 'adaptör']):
            cat = 'Teknoloji'
        elif any(w in tl for w in ['krem', 'serum', 'parfüm', 'güneş', 'bb krem', 'nemlendirici', 'şampuan']):
            cat = 'Kozmetik'
        elif any(w in tl for w in ['tava', 'tencere', 'termos', 'pike', 'bardak', 'yastık', 'bıçak', 'nevresim']):
            cat = 'Ev & Yaşam'
        elif any(w in tl for w in ['mont', 'ceket', 'çanta', 'kravat', 'çorap', 'pantolon', 'ayakkabı', 'gözlük', 'sweatshirt']):
            cat = 'Moda'
        else:
            return None
    
    try:
        orig = round(float(item.get('originalPrice') or item.get('oldPrice') or 0), 2)
        disc = round(float(item.get('discountedPrice') or item.get('price') or 0), 2)
    except Exception:
        return None
        
    if orig <= 0 or disc <= 0 or disc >= orig:
        return None
        
    rate = int(round((1 - disc / orig) * 100))
    if rate < 15:
        return None
        
    if not url.startswith('http') or not img.startswith('http'):
        return None
        
    asin = ''
    m = re.search(r'/dp/([B0-9A-Z]{10})', url)
    if m:
        asin = m.group(1)
        url = f"https://www.amazon.com.tr/dp/{asin}"
    elif default_store == 'Amazon TR':
        return None # Require real ASIN for Amazon
        
    item_id = item.get('id') or (f"amz-{asin}" if asin else f"{default_store[:3].lower()}-{abs(hash(title))%1000000:06d}")
    
    return {
        'id': str(item_id),
        'title': title,
        'originalPrice': orig,
        'discountedPrice': disc,
        'discountRate': rate,
        'imageUrl': img,
        'productUrl': url,
        'store': default_store,
        'category': cat
    }

# Build pools
amz_pool = {c: [] for c in CATEGORIES}
hb_pool = {c: [] for c in CATEGORIES}
idf_pool = {c: [] for c in CATEGORIES}

seen_urls = set()
seen_titles = set()

# 1. Collect Amazon deals
amz_files = [
    'scraper/amazon_strictly_live_deals.json',
    'scraper/amazon_verified_deals.json',
    'scraper/amz_test_results.json',
    'scraper/top_brand_amz_moda.json',
    'scraper/discovered_live_amazon.json',
    'scraper/yaniyo_amazon_deals.json'
]
for p in amz_files:
    if not os.path.exists(p): continue
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
            items = data if isinstance(data, list) else data.values()
            for it in items:
                cl = clean_item(it, 'Amazon TR')
                if cl and cl['productUrl'] not in seen_urls and cl['title'].lower() not in seen_titles:
                    seen_urls.add(cl['productUrl'])
                    seen_titles.add(cl['title'].lower())
                    amz_pool[cl['category']].append(cl)
    except Exception as e:
        print(f"Error reading {p}: {e}")

# 2. Collect Hepsiburada deals
hb_files = [
    'scraper/hb_harvested_fresh.json',
    'scraper/hepsiburada_verified_deals.json',
    'scraper/final_verified_catalog.json'
]
for p in hb_files:
    if not os.path.exists(p): continue
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                for cat, items in data.items():
                    for it in items:
                        cl = clean_item(it, 'Hepsiburada', default_cat=cat)
                        if cl and cl['store'] == 'Hepsiburada' and cl['productUrl'] not in seen_urls and cl['title'].lower() not in seen_titles:
                            seen_urls.add(cl['productUrl'])
                            seen_titles.add(cl['title'].lower())
                            hb_pool[cl['category']].append(cl)
            elif isinstance(data, list):
                for it in data:
                    if it.get('store') == 'Hepsiburada':
                        cl = clean_item(it, 'Hepsiburada')
                        if cl and cl['productUrl'] not in seen_urls and cl['title'].lower() not in seen_titles:
                            seen_urls.add(cl['productUrl'])
                            seen_titles.add(cl['title'].lower())
                            hb_pool[cl['category']].append(cl)
    except Exception as e:
        print(f"Error reading {p}: {e}")

# 3. Collect Idefix deals
idf_files = [
    'scraper/idefix_all_categories.json',
    'scraper/all_tech_verified.json',
    'scraper/top_home_strict.json',
    'scraper/home_beauty_strict.json',
    'scraper/final_verified_catalog.json'
]
for p in idf_files:
    if not os.path.exists(p): continue
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
            items = data if isinstance(data, list) else data.values()
            for it in items:
                store = it.get('store', 'Idefix')
                if store != 'Idefix': continue
                cl = clean_item(it, 'Idefix')
                if cl and cl['productUrl'] not in seen_urls and cl['title'].lower() not in seen_titles:
                    seen_urls.add(cl['productUrl'])
                    seen_titles.add(cl['title'].lower())
                    idf_pool[cl['category']].append(cl)
    except Exception as e:
        print(f"Error reading {p}: {e}")

print("--- POOL STATUS ---")
print("Amazon TR:")
for c in CATEGORIES:
    print(f"  {c}: {len(amz_pool[c])}")
print("Hepsiburada:")
for c in CATEGORIES:
    print(f"  {c}: {len(hb_pool[c])}")
print("Idefix:")
for c in CATEGORIES:
    print(f"  {c}: {len(idf_pool[c])}")

with open('backend/pool/pool_amazon.json', 'w', encoding='utf-8') as f:
    json.dump(amz_pool, f, ensure_ascii=False, indent=2)
with open('backend/pool/pool_hepsiburada.json', 'w', encoding='utf-8') as f:
    json.dump(hb_pool, f, ensure_ascii=False, indent=2)
with open('backend/pool/pool_idefix.json', 'w', encoding='utf-8') as f:
    json.dump(idf_pool, f, ensure_ascii=False, indent=2)

print("\nSaved pools to backend/pool/")
