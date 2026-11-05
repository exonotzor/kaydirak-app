import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json
import time
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import os

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

queries = [
    # Teknoloji
    ('Teknoloji', 'bluetooth kulaklik'),
    ('Teknoloji', 'kablosuz kulaklik'),
    ('Teknoloji', 'tws kulaklik'),
    ('Teknoloji', 'gaming kulaklik'),
    ('Teknoloji', 'oyuncu mouse'),
    ('Teknoloji', 'rgb mouse'),
    ('Teknoloji', 'mekanik klavye'),
    ('Teknoloji', 'oyuncu klavye'),
    ('Teknoloji', 'powerbank 20000mah'),
    ('Teknoloji', 'powerbank 10000mah'),
    ('Teknoloji', 'hizli sarj adaptoru'),
    ('Teknoloji', 'usb bellek 64gb'),
    ('Teknoloji', 'tasinabilir ssd'),
    ('Teknoloji', 'bluetooth hoparlor'),
    ('Teknoloji', 'akilli saat'),
    ('Teknoloji', 'akilli bileklik'),
    ('Teknoloji', 'laptop sogutucu'),
    ('Teknoloji', 'oyun kolu gamepad'),

    # Moda
    ('Moda', 'erkek mont'),
    ('Moda', 'kadin mont'),
    ('Moda', 'erkek sweatshirt'),
    ('Moda', 'kadin sweatshirt'),
    ('Moda', 'erkek kazak'),
    ('Moda', 'kadin kazak'),
    ('Moda', 'erkek gomlek'),
    ('Moda', 'kadin trenckot'),
    ('Moda', 'erkek yagmurluk'),
    ('Moda', 'kadin hirka'),
    ('Moda', 'spor ayakkabi erkek'),
    ('Moda', 'spor ayakkabi kadin'),
    ('Moda', 'kosu ayakkabisi'),
    ('Moda', 'sirt cantasi'),
    ('Moda', 'omuz cantasi'),
    ('Moda', 'erkek ceket'),
    ('Moda', 'kadin ceket'),

    # Ev & Yaşam
    ('Ev & Yaşam', 'tencere seti'),
    ('Ev & Yaşam', 'granit tava'),
    ('Ev & Yaşam', 'dokum tava'),
    ('Ev & Yaşam', 'bicak seti'),
    ('Ev & Yaşam', 'termos mug'),
    ('Ev & Yaşam', 'stanley termos'),
    ('Ev & Yaşam', 'kahve fincan takimi'),
    ('Ev & Yaşam', 'su takimi bardak'),
    ('Ev & Yaşam', 'nevresim takimi cift kisilik'),
    ('Ev & Yaşam', 'pamuk nevresim'),
    ('Ev & Yaşam', 'banyo havlusu'),
    ('Ev & Yaşam', 'yastik seti'),
    ('Ev & Yaşam', 'saklama kabi seti'),
    ('Ev & Yaşam', 'baharatlik seti'),
    ('Ev & Yaşam', 'french press kahve'),

    # Kozmetik
    ('Kozmetik', 'gunes kremi spf 50'),
    ('Kozmetik', 'nemlendirici yuz kremi'),
    ('Kozmetik', 'hyaluronik asit serum'),
    ('Kozmetik', 'c vitamini serum'),
    ('Kozmetik', 'goz cevresi kremi'),
    ('Kozmetik', 'parfum edp erkek'),
    ('Kozmetik', 'parfum edp kadin'),
    ('Kozmetik', 'sac dokulmesine karsi sampuan'),
    ('Kozmetik', 'keratin sac maskesi'),
    ('Kozmetik', 'micellar temizleme suyu'),
    ('Kozmetik', 'dudak balmi'),
    ('Kozmetik', 'vucut losyonu'),
    ('Kozmetik', 'el kremi'),
]

existing_deals = []
if os.path.exists('scraper/hepsiburada_verified_deals.json'):
    with open('scraper/hepsiburada_verified_deals.json', 'r', encoding='utf-8') as f:
        existing_deals = json.load(f)

print(f"Loaded {len(existing_deals)} existing verified Hepsiburada deals.", flush=True)
seen_urls = set(x['productUrl'] for x in existing_deals)
seen_titles = set(x['title'][:25].lower() for x in existing_deals)

def search_query(item):
    cat, q = item
    search_url = f"https://www.hepsiburada.com/ara?q={requests.utils.quote(q)}"
    items = []
    try:
        r = requests.get(search_url, headers=headers, verify=False, timeout=8)
        if r.status_code == 200:
            found_paths = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', r.text)
            unique_paths = list(dict.fromkeys(found_paths))
            for p in unique_paths[:20]:
                full_url = 'https://www.hepsiburada.com' + p.split('?')[0]
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                items.append((cat, full_url))
            print(f"  [{cat}] '{q}': found {len(items)} new candidate links", flush=True)
    except Exception as e:
        print(f"  [{cat}] '{q}' error: {e}", flush=True)
    return items

print("Searching Hepsiburada categories concurrently...", flush=True)
all_pdp_targets = []
with ThreadPoolExecutor(max_workers=6) as ex:
    for res in ex.map(search_query, queries):
        all_pdp_targets.extend(res)

print(f"\nTotal candidate PDPs to verify: {len(all_pdp_targets)}", flush=True)

def verify_hb_pdp(target):
    cat, url = target
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=7)
        if r.status_code != 200 or len(r.text) < 15000:
            return None
            
        soup = BeautifulSoup(r.text, 'html.parser')
        h1 = soup.find('h1')
        title = h1.get_text().strip() if h1 else ''
        if not title or len(title) < 5 or 'Güvenlik' in title or 'Sayfa Bulunamadı' in title:
            # Fallback to meta title
            meta_t = soup.find('title')
            title = meta_t.get_text().strip() if meta_t else ''
            if ' - Hepsiburada' in title:
                title = title.split(' - Hepsiburada')[0].strip()
                
        if not title or len(title) < 5:
            return None
            
        title = re.sub(r'\s+', ' ', title).strip()
        t_prefix = title[:25].lower()
        if t_prefix in seen_titles:
            return None
        
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
                    }
    except Exception:
        pass
    return None

print("\nVerifying Hepsiburada PDPs with 20 threads...", flush=True)
verified_hb = list(existing_deals)
with ThreadPoolExecutor(max_workers=20) as ex:
    for res in ex.map(verify_hb_pdp, all_pdp_targets):
        if res:
            if not any(x['id'] == res['id'] or x['productUrl'] == res['productUrl'] for x in verified_hb):
                verified_hb.append(res)
                seen_titles.add(res['title'][:25].lower())
                print(f"[{res['category']}] %{res['discountRate']} | {res['discountedPrice']} TL (was {res['originalPrice']} TL) | {res['title'][:38]}", flush=True)

print(f"\nTotal verified Hepsiburada deals: {len(verified_hb)}", flush=True)
print(Counter(x['category'] for x in verified_hb), flush=True)

with open('scraper/hepsiburada_verified_deals.json', 'w', encoding='utf-8') as f:
    json.dump(verified_hb, f, ensure_ascii=False, indent=2)
print("Saved to scraper/hepsiburada_verified_deals.json", flush=True)
