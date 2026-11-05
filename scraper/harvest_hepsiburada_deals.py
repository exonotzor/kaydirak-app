import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json
import time
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

queries = [
    # Teknoloji
    ('Teknoloji', 'bluetooth kulaklik'),
    ('Teknoloji', 'akilli saat'),
    ('Teknoloji', 'oyuncu mouse'),
    ('Teknoloji', 'powerbank'),
    ('Teknoloji', 'kablosuz hoparlor'),
    ('Teknoloji', 'gaming kulaklik'),
    ('Teknoloji', 'mekanik klavye'),
    ('Teknoloji', 'sarj cihazi'),
    
    # Moda
    ('Moda', 'erkek mont'),
    ('Moda', 'kadin mont'),
    ('Moda', 'spor ayakkabi'),
    ('Moda', 'sweatshirt'),
    ('Moda', 'erkek gomlek'),
    ('Moda', 'sirt cantasi'),
    ('Moda', 'erkek kazak'),
    ('Moda', 'kadin ceket'),
    
    # Ev & Yaşam
    ('Ev & Yaşam', 'tencere seti'),
    ('Ev & Yaşam', 'termos'),
    ('Ev & Yaşam', 'tava seti'),
    ('Ev & Yaşam', 'bicak seti'),
    ('Ev & Yaşam', 'nevresim takimi'),
    ('Ev & Yaşam', 'mutfak gerecleri'),
    ('Ev & Yaşam', 'dokum tava'),
    ('Ev & Yaşam', 'kahve kupasi'),
    
    # Kozmetik
    ('Kozmetik', 'gunes kremi'),
    ('Kozmetik', 'parfum'),
    ('Kozmetik', 'yuz serumu'),
    ('Kozmetik', 'nemlendirici krem'),
    ('Kozmetik', 'sampuan'),
    ('Kozmetik', 'goz kremi'),
    ('Kozmetik', 'sac maskesi'),
]

def get_category_links(cat, q):
    search_url = f"https://www.hepsiburada.com/ara?q={requests.utils.quote(q)}"
    items = []
    try:
        r = requests.get(search_url, headers=headers, verify=False, timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            links = soup.find_all('a', href=re.compile(r'-p(m)?-[A-Za-z0-9]+'))
            seen = set()
            for a in links[:15]:
                href = a.get('href', '')
                if href.startswith('/'):
                    href = 'https://www.hepsiburada.com' + href
                if href in seen:
                    continue
                seen.add(href)
                title = a.get('title') or a.get_text().strip()
                img = a.find('img')
                img_src = img.get('src') if img else None
                items.append((cat, href, title, img_src))
    except Exception as e:
        print(f"Error searching {q}: {e}")
    return items

print("Searching Hepsiburada categories...", flush=True)
all_pdp_targets = []
for cat, q in queries:
    all_pdp_targets.extend(get_category_links(cat, q))
    time.sleep(0.2)

print(f"Total Hepsiburada candidate PDPs found: {len(all_pdp_targets)}", flush=True)

def verify_hb_pdp(target):
    cat, url, fallback_title, fallback_img = target
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=7)
        if r.status_code != 200 or len(r.text) < 20000:
            return None
            
        soup = BeautifulSoup(r.text, 'html.parser')
        h1 = soup.find('h1')
        title = h1.get_text().strip() if h1 else fallback_title
        if not title or len(title) < 5 or 'Güvenlik' in title or 'Sayfa Bulunamadı' in title:
            return None
            
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Extract images
        img_url = fallback_img
        if not img_url:
            imgs = re.findall(r'https://productimages\.hepsiburada\.net/s/[^\s"\'<>]+\.jpg', r.text)
            if imgs:
                img_url = imgs[0].split('?')[0].split('"')[0]
                
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
                    sku_match = re.search(r'-p(m)?-([A-Za-z0-9]+)', url)
                    sku = sku_match.group(2) if sku_match else str(abs(hash(url)))[:10]
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

print("Verifying Hepsiburada PDPs with 15 threads...", flush=True)
verified_hb = []
with ThreadPoolExecutor(max_workers=15) as ex:
    for res in ex.map(verify_hb_pdp, all_pdp_targets):
        if res:
            if not any(x['id'] == res['id'] for x in verified_hb):
                verified_hb.append(res)
                print(f"[{res['category']}] %{res['discountRate']} | {res['discountedPrice']} TL (was {res['originalPrice']} TL) | {res['title'][:40]}", flush=True)

print(f"\nTotal verified Hepsiburada deals: {len(verified_hb)}", flush=True)
from collections import Counter
print(Counter(x['category'] for x in verified_hb), flush=True)

with open('scraper/hepsiburada_verified_deals.json', 'w', encoding='utf-8') as f:
    json.dump(verified_hb, f, ensure_ascii=False, indent=2)
print("Saved to scraper/hepsiburada_verified_deals.json", flush=True)
