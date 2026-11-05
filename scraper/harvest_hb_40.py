import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import os
import sys

# UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

queries = [
    # Teknoloji
    ('Teknoloji', 'oyuncu mouse'),
    ('Teknoloji', 'mekanik klavye'),
    ('Teknoloji', 'powerbank 20000mah'),
    ('Teknoloji', 'akilli saat'),
    ('Teknoloji', 'bluetooth hoparlor'),
    ('Teknoloji', 'hizli sarj adaptoru'),
    ('Teknoloji', 'gaming kulaklik'),
    ('Teknoloji', 'laptop sogutucu'),
    ('Teknoloji', 'tasinabilir ssd'),
    ('Teknoloji', 'webcam'),
    
    # Moda
    ('Moda', 'erkek mont'),
    ('Moda', 'kadin ceket'),
    ('Moda', 'spor ayakkabi'),
    ('Moda', 'sweatshirt'),
    ('Moda', 'sirt cantasi'),
    ('Moda', 'erkek polar'),
    ('Moda', 'kadin trenckot'),
    ('Moda', 'esofman takimi'),
    ('Moda', 'erkek kazak'),
    ('Moda', 'kadin hirka'),

    # Ev & Yaşam
    ('Ev & Yaşam', 'granit tava'),
    ('Ev & Yaşam', 'bicak seti'),
    ('Ev & Yaşam', 'kahve fincan takimi'),
    ('Ev & Yaşam', 'nevresim takimi'),
    ('Ev & Yaşam', 'banyo havlusu'),
    ('Ev & Yaşam', 'saklama kabi seti'),
    ('Ev & Yaşam', 'baharatlik takimi'),
    ('Ev & Yaşam', 'cam cay bardagi takimi'),
    ('Ev & Yaşam', 'dokum tencere'),
    ('Ev & Yaşam', 'borcam tepsi'),

    # Kozmetik
    ('Kozmetik', 'gunes kremi spf 50'),
    ('Kozmetik', 'hyaluronik asit serum'),
    ('Kozmetik', 'c vitamini serum'),
    ('Kozmetik', 'nemlendirici yuz kremi'),
    ('Kozmetik', 'parfum edp erkek'),
    ('Kozmetik', 'parfum edp kadin'),
    ('Kozmetik', 'goz cevresi kremi'),
    ('Kozmetik', 'sac maskesi keratin'),
    ('Kozmetik', 'micellar temizleme suyu'),
    ('Kozmetik', 'vucut losyonu'),
]

# Load existing HB deals
existing_hb = []
if os.path.exists('scraper/hepsiburada_verified_deals.json'):
    with open('scraper/hepsiburada_verified_deals.json', 'r', encoding='utf-8') as f:
        existing_hb = json.load(f)

print(f"Loaded {len(existing_hb)} existing HB deals.", flush=True)

def extract_brand_and_type(title):
    t = title.lower()
    brand = 'diger'
    for b in ['xiaomi', 'redmi', 'logitech', 'havit', 'adidas', 'u.s. polo', 'us polo', 'hascevher', 'stanley', 'victorinox', 'english home', 'philips', 'samsung', 'karaca', 'tefal', 'nivea', 'loreal', "l'oreal", 'garnier', 'colgate', 'taç', 'tac', 'defacto', 'koton', 'mavi', 'puma', 'nike', 'columbia', 'under armour', 'spovan', 'casio', 'baseus', 'anker', 'jbl', 'apple', 'honor', 'lenovo', 'asus', 'hp', 'dell', 'tp-link', 'd-link', 'neutrogena', 'cerave', 'la roche', 'bargello', 'eyup sabri', 'arko']:
        if b in t:
            brand = b.replace(' ', '').replace('.', '').replace("'", '')
            break
    if brand == 'diger':
        brand = t.split()[0] if t.split() else 'unknown'

    ptype = 'diger'
    for pt in ['kulaklik', 'kulaklık', 'mouse', 'klavye', 'powerbank', 'saat', 'hoparlor', 'hoparlör', 'adaptor', 'adaptör', 'kablo', 'ssd', 'kamera', 'webcam', 'sogutucu', 'soğutucu', 'mont', 'ceket', 'kaban', 'trenckot', 'trençkot', 'polar', 'yelek', 'hirka', 'hırka', 'kazak', 'sweatshirt', 'gomlek', 'gömlek', 'tshirt', 'tişört', 'pantolon', 'esofman', 'eşofman', 'ayakkabi', 'ayakkabı', 'sneaker', 'bot', 'canta', 'çanta', 'tava', 'tencere', 'bicak', 'bıçak', 'termos', 'fincan', 'bardak', 'nevresim', 'havlu', 'bornoz', 'yastik', 'yastık', 'krem', 'serum', 'parfum', 'parfüm', 'sampuan', 'şampuan', 'maske', 'losyon', 'sabun']:
        if pt in t:
            ptype = pt.replace('ı', 'i').replace('ş', 's').replace('ç', 'c').replace('ö', 'o').replace('ü', 'u').replace('ğ', 'g')
            break
    return brand, ptype

# Filter existing to keep at most 1 per (brand, type)
filtered_hb = []
seen_brand_types = set()
for d in existing_hb:
    brand, ptype = extract_brand_and_type(d['title'])
    key = f"{brand}_{ptype}"
    if key not in seen_brand_types:
        seen_brand_types.add(key)
        d['brand_type'] = key
        filtered_hb.append(d)
        print(f"Kept existing: [{d['category']}] {key} | {d['title'][:40]}", flush=True)

print(f"\nExisting diverse HB deals kept: {len(filtered_hb)}", flush=True)

# Collect new candidate PDPs
candidates = []
seen_urls = set(x['productUrl'] for x in filtered_hb)

for cat, q in queries:
    search_url = f"https://www.hepsiburada.com/ara?q={requests.utils.quote(q)}"
    try:
        r = requests.get(search_url, headers=headers, verify=False, timeout=6)
        if r.status_code == 200:
            found = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', r.text)
            unique = list(dict.fromkeys(found))
            added = 0
            for u in unique[:12]:
                full_url = 'https://www.hepsiburada.com' + u.split('?')[0]
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    candidates.append((cat, full_url))
                    added += 1
            print(f"[{cat}] '{q}': +{added} candidate PDPs", flush=True)
        time.sleep(0.1)
    except Exception as e:
        print(f"Error {q}: {e}", flush=True)

print(f"\nTotal candidate PDPs to verify: {len(candidates)}", flush=True)

def verify_single_pdp(item):
    cat, url = item
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=6)
        if r.status_code != 200 or len(r.text) < 15000:
            return None
            
        soup = BeautifulSoup(r.text, 'html.parser')
        h1 = soup.find('h1')
        title = h1.get_text().strip() if h1 else ''
        if not title or len(title) < 5 or 'Güvenlik' in title or 'Sayfa Bulunamadı' in title:
            meta_t = soup.find('title')
            title = meta_t.get_text().strip() if meta_t else ''
            if ' - Hepsiburada' in title:
                title = title.split(' - Hepsiburada')[0].strip()
                
        if not title or len(title) < 5:
            return None
            
        title = re.sub(r'\s+', ' ', title).strip()
        brand, ptype = extract_brand_and_type(title)
        
        # Extract images
        imgs = re.findall(r'https://productimages\.hepsiburada\.net/s/[^\s"\'<>]+\.jpg', r.text)
        img_url = None
        if imgs:
            for im in imgs:
                clean_im = im.split('?')[0].split('"')[0].replace('{size}', '550')
                if '300-400' in clean_im or '550' in clean_im or '/s/' in clean_im:
                    img_url = clean_im
                    break
            if not img_url:
                img_url = imgs[0].split('?')[0].split('"')[0].replace('{size}', '550')
                
        if not img_url:
            return None
            
        # Extract prices
        p_boxes = soup.select('span[data-test-id="variant-box-price"], [data-test-id="default-price"], del, [class*="Price"], [class*="price"]')
        extracted_prices = []
        for pb in p_boxes:
            txt = pb.get_text().strip()
            matches = re.findall(r'((?:\d{1,3}\.)*\d+,\d{2})', txt)
            for m in matches:
                try:
                    val = float(m.replace('.', '').replace(',', '.'))
                    extracted_prices.append(val)
                except Exception:
                    pass
                    
        extracted_prices = sorted(list(set(extracted_prices)))
        if len(extracted_prices) < 2:
            all_txt_matches = re.findall(r'((?:\d{1,3}\.)*\d+,\d{2}\s*(?:TL|₺))', r.text)
            for atm in all_txt_matches:
                m = re.search(r'((?:\d{1,3}\.)*\d+,\d{2})', atm)
                if m:
                    try:
                        val = float(m.group(1).replace('.', '').replace(',', '.'))
                        extracted_prices.append(val)
                    except Exception:
                        pass
            extracted_prices = sorted(list(set(extracted_prices)))
            
        if len(extracted_prices) >= 2:
            p_sale = extracted_prices[0]
            p_orig = None
            for p in extracted_prices[1:]:
                ratio = p / p_sale
                if 1.15 <= ratio <= 3.5:
                    p_orig = p
                    break
                    
            if p_orig and p_orig > p_sale:
                rate = round(((p_orig - p_sale) / p_orig) * 100)
                if 15 <= rate <= 80:
                    sku_match = re.search(r'-p(?:m)?-([A-Za-z0-9]+)', url)
                    sku = sku_match.group(1) if sku_match else str(abs(hash(url)))[:10]
                    
                    return {
                        'id': f"hb-{sku}",
                        'title': title,
                        'category': cat,
                        'store': 'Hepsiburada',
                        'originalPrice': p_orig,
                        'discountedPrice': p_sale,
                        'discountRate': rate,
                        'productUrl': url,
                        'imageUrl': img_url,
                        'brand': brand,
                        'ptype': ptype,
                        'brand_type': f"{brand}_{ptype}"
                    }
    except Exception:
        pass
    return None

print("\nVerifying PDPs concurrently with 15 threads...", flush=True)
verified_pool = []
with ThreadPoolExecutor(max_workers=15) as ex:
    for res in ex.map(verify_single_pdp, candidates):
        if res:
            key = res['brand_type']
            if key not in seen_brand_types:
                seen_brand_types.add(key)
                verified_pool.append(res)
                print(f"✅ Verified [{res['category']}] %{res['discountRate']} | {res['discountedPrice']} TL (was {res['originalPrice']} TL) | {res['brand']} {res['ptype']} | {res['title'][:35]}", flush=True)
                if len(filtered_hb) + len(verified_pool) >= 48:
                    break

total_hb = filtered_hb + verified_pool
print(f"\nTotal Verified Diverse Hepsiburada Deals: {len(total_hb)}", flush=True)
print(Counter(x['category'] for x in total_hb), flush=True)

with open('scraper/hepsiburada_verified_deals.json', 'w', encoding='utf-8') as f:
    json.dump(total_hb, f, ensure_ascii=False, indent=2)
print("Saved to scraper/hepsiburada_verified_deals.json", flush=True)
