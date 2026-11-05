import json
import os
import re
import sys
import time
import urllib3
import requests as std_requests
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup
from backend.build_bestseller_pools import (
    SUBCATEGORIES, clean_title, is_valid_for_category,
    compute_prices, parse_tr_price, verify_pool_images
)

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

urllib3.disable_warnings()

# 1. Top up the first 4 Amazon Teknoloji subcategories with session warmup
with open('backend/pool/pool_amazon.json', 'r', encoding='utf-8') as f:
    amz_pool = json.load(f)

seen_asins = {it['id'].replace('amz-', '') for cat_items in amz_pool.values() for it in cat_items}
seen_titles = {it['title'].lower()[:45] for cat_items in amz_pool.values() for it in cat_items}

session = cffi_requests.Session()
headers = {'Accept-Language': 'tr-TR,tr;q=0.9', 'Referer': 'https://www.amazon.com.tr/'}
session.get('https://www.amazon.com.tr/', impersonate='chrome120', headers=headers, timeout=10, verify=False)

missing_tech_subcats = SUBCATEGORIES['Teknoloji'][:4]
new_amz_tech = []
for subcat_name, queries in missing_tech_subcats:
    subcat_count = 0
    for q in queries:
        if subcat_count >= 14:
            break
        url = f"https://www.amazon.com.tr/s?k={std_requests.utils.quote(q)}&s=exact-aware-popularity-rank"
        for attempt in range(3):
            r = session.get(url, impersonate='chrome120', headers=headers, timeout=10, verify=False)
            soup = BeautifulSoup(r.text, 'html.parser')
            cards = soup.select('div.s-result-item[data-asin]')
            if len(cards) > 5:
                break
            time.sleep(0.5)
        for card in cards:
            if subcat_count >= 14:
                break
            asin = (card.get('data-asin') or '').strip()
            if len(asin) != 10 or not asin.startswith('B0') or asin in seen_asins:
                continue
            if 'Sponsorlu' in card.get_text():
                continue
            img_el = card.select_one('img.s-image')
            if not img_el:
                continue
            img_url = (img_el.get('src') or '').strip()
            if not img_url.startswith('https://m.media-amazon.com/images/I/') or not img_url.endswith('.jpg') or '.js' in img_url:
                continue
            img_url = re.sub(r'\._AC_[^.]+_\.jpg$', '._AC_UL500_.jpg', img_url)
            title = clean_title(img_el.get('alt') or '')
            if not is_valid_for_category(title, 'Teknoloji') or title.lower()[:45] in seen_titles:
                continue
            price_el = card.select_one('span.a-price:not([data-a-strike]) span.a-offscreen')
            if not price_el:
                continue
            sale_val = parse_tr_price(price_el.get_text())
            old_el = card.select_one('span.a-price[data-a-strike] span.a-offscreen')
            orig_val = parse_tr_price(old_el.get_text()) if old_el else 0.0
            orig, disc, rate = compute_prices(orig_val, sale_val, asin)
            if not orig:
                continue
            seen_asins.add(asin)
            seen_titles.add(title.lower()[:45])
            subcat_count += 1
            new_amz_tech.append({
                'id': f'amz-{asin}',
                'title': title,
                'originalPrice': orig,
                'discountedPrice': disc,
                'discountRate': rate,
                'imageUrl': img_url,
                'productUrl': f'https://www.amazon.com.tr/dp/{asin}',
                'store': 'Amazon TR',
                'category': 'Teknoloji',
                'subCategory': subcat_name
            })
        time.sleep(0.25)
    print(f"  [Amazon TR Top-Up] Teknoloji -> {subcat_name}: +{subcat_count} items")

# Verify only the newly added Amazon Teknoloji items
temp_pool = {c: [] for c in SUBCATEGORIES}
temp_pool['Teknoloji'] = new_amz_tech
verified_new = verify_pool_images(temp_pool, 'Amazon TR Top-Up')
amz_pool['Teknoloji'] = verified_new['Teknoloji'] + amz_pool['Teknoloji']
with open('backend/pool/pool_amazon.json', 'w', encoding='utf-8') as f:
    json.dump(amz_pool, f, ensure_ascii=False, indent=2)
print(f"Updated Amazon TR pool: { {c: len(amz_pool[c]) for c in SUBCATEGORIES} }")

# 2. Harvest Idefix Best Sellers across 32 Official Category URLs
IDEFIX_SUBCATEGORIES = {
    'Teknoloji': [
        ('Kulaklık', ['/gaming-kulaklik-c-230890672']),
        ('Mouse & Klavye', ['/gaming-mouse-c-230861751', '/gaming-klavye-c-230835467']),
        ('Bilgisayar & Tablet', ['/bilgisayar-ve-tablet-c-2302']),
        ('Akıllı Saat', ['/akilli-saatler-smartwatch-c-230993929', '/giyilebilir-teknoloji-c-2309']),
        ('Hoparlör & Ses', ['/tv-goruntu-ses-c-2314']),
        ('Oyuncu Ekipmanları', ['/oyuncu-donanimlari-c-2308115310', '/pc-joystick-gamepad-aksesuarlari-c-230865728']),
        ('Webcam & Foto', ['/foto-kamera-c-2307', '/yayinci-aksesuarlari-c-230898265']),
        ('Konsol & Elektronik', ['/konsol-aksesuarlari-c-2308758120', '/teknoloji-c-23'])
    ],
    'Moda': [
        ('Erkek Üst Giyim', ['/erkek-giyim-c-5507240150']),
        ('Kadın Giyim', ['/kadin-elbise-c-550916706', '/kadin-gomlek-ve-bluzlar-l-13257']),
        ('Dış Giyim', ['/kadin-ceket-c-5509692200', '/kadin-hirka-c-550910384', '/kadin-sweatshirt-c-550952755']),
        ('Spor Ayakkabı', ['/sneaker-c-550342261']),
        ('Günlük Ayakkabı', ['/gunluk-ayakkabi-c-550327518', '/bot-c-550371009']),
        ('Çanta & Sırt Çantası', ['/cantalar-valizler-c-5511']),
        ('Saat & Gözlük', ['/saat-c-5501500910', '/gozlukler-c-5508']),
        ('Alt Giyim & Aksesuar', ['/kadin-jean-c-550963769', '/kadin-pantolon-c-550976511'])
    ],
    'Ev & Yaşam': [
        ('Kahve Keyfi', ['/kahve-hazirlama-c-2311805100', '/tam-otomatik-kahve-makineleri-c-231189131']),
        ('Küçük Ev Aletleri', ['/gida-hazirlama-c-2311970490', '/icecek-hazirlama-c-2311382370']),
        ('Pişirme & Tencere', ['/gida-pisirme-c-2311348910', '/sofra-mutfak-c-2206']),
        ('Termos & Matara', ['/termos-mataralar-c-770532183']),
        ('Sofra & Mutfak', ['/yemek-takimlari-c-220624792', '/ev-gerecleri-c-2203']),
        ('Ev Tekstili', ['/ev-tekstili-c-2204', '/ev-dekorasyon-c-2202']),
        ('Ütü & Süpürge', ['/utuler-c-2311258000', '/dikey-supurge-c-231175430', '/robot-supurge-c-2311110060']),
        ('Aydınlatma & Kamp', ['/aydinlatma-c-2201', '/kamp-sandalyesi-c-770573348', '/elektrikli-el-aletleri-c-5303500630'])
    ],
    'Kozmetik': [
        ('Parfüm', ['/parfum-ve-deodorant-c-4403992550', '/roll-on-ve-stick-c-440322972']),
        ('Cilt Serumu', ['/kore-kozmetik-l-42012', '/cilt-bakim-c-4403999870']),
        ('Yüz Bakımı', ['/bb-kremler-c-440367703', '/kapatici-c-440344466']),
        ('Güneş Bakımı', ['/gunes-urunleri-c-4403980570']),
        ('Saç Bakımı', ['/sampuanlar-c-440243234', '/sac-maskeleri-bakim-krem-losyon-ve-spreyleri-c-440226781']),
        ('Makyaj', ['/maskara-c-440319818', '/rujlar-c-440344872', '/fondoten-c-440312986']),
        ('Kişisel Bakım Cihazı', ['/elektrikli-kisisel-bakim-aletleri-c-2316', '/sac-kurutma-makineleri-c-2316702316']),
        ('Vücut Bakımı', ['/agiz-bakim-c-4402630750', '/kisisel-bakim-c-4402'])
    ]
}

print("\n=== HARVESTING IDEFIX BEST SELLERS ACROSS 32 SUB-CATEGORIES ===")
idf_pool = {cat: [] for cat in SUBCATEGORIES}
seen_idf_ids = set()
seen_idf_titles = set()
idf_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9'
}

for cat, subcats in IDEFIX_SUBCATEGORIES.items():
    for subcat_name, paths in subcats:
        subcat_count = 0
        for p_url in paths:
            if subcat_count >= 14:
                break
            sep = '&' if '?' in p_url else '?'
            full_url = f"https://www.idefix.com{p_url}{sep}siralama=desc_score_best_selling"
            try:
                r = std_requests.get(full_url, headers=idf_headers, verify=False, timeout=8)
                if r.status_code != 200 or '__NEXT_DATA__' not in r.text:
                    continue
                soup = BeautifulSoup(r.text, 'html.parser')
                s = soup.find('script', id='__NEXT_DATA__')
                if not s or not s.string:
                    continue
                d = json.loads(s.string)
                pp = d.get('props', {}).get('pageProps', {})
                items = (pp.get('categoryData') or {}).get('items') or (pp.get('landingData') or {}).get('items') or []
                for it in items:
                    if subcat_count >= 14:
                        break
                    variants = it.get('variants') or [it]
                    v = variants[0]
                    vid = str(v.get('id') or it.get('id') or '').strip()
                    title = clean_title(v.get('name') or it.get('name') or '')
                    if not vid or vid in seen_idf_ids or not is_valid_for_category(title, cat):
                        continue
                    if title.lower()[:45] in seen_idf_titles:
                        continue
                    handle = (v.get('handleUrl') or it.get('handleUrl') or '').strip().lstrip('/')
                    if not handle:
                        continue
                    prod_url = f"https://www.idefix.com/{handle}"
                    imgs = v.get('images') or it.get('images') or []
                    if not imgs:
                        continue
                    img_url = (imgs[0].get('src') or '').replace('{size}', '600/600/').strip()
                    if not img_url.startswith('https://'):
                        continue
                    orig_val = max(float(v.get('price') or 0), float(v.get('thirtyDaysLowPrice') or 0))
                    sale_val = float(v.get('discountedSalesPrice') or v.get('price') or 0)
                    orig, disc, rate = compute_prices(orig_val, sale_val, vid)
                    if not orig:
                        continue
                    seen_idf_ids.add(vid)
                    seen_idf_titles.add(title.lower()[:45])
                    subcat_count += 1
                    idf_pool[cat].append({
                        'id': f'idefix-{vid}',
                        'title': title,
                        'originalPrice': orig,
                        'discountedPrice': disc,
                        'discountRate': rate,
                        'imageUrl': img_url,
                        'productUrl': prod_url,
                        'store': 'Idefix',
                        'category': cat,
                        'subCategory': subcat_name
                    })
                time.sleep(0.15)
            except Exception as e:
                print(f"  [Idefix Error] {p_url}: {e}")
        print(f"  [Idefix] {cat} -> {subcat_name}: +{subcat_count} items (Total {cat}: {len(idf_pool[cat])})")

idf_pool = verify_pool_images(idf_pool, 'Idefix')
with open('backend/pool/pool_idefix.json', 'w', encoding='utf-8') as f:
    json.dump(idf_pool, f, ensure_ascii=False, indent=2)
print(f"Updated Idefix pool: { {c: len(idf_pool[c]) for c in SUBCATEGORIES} }")
