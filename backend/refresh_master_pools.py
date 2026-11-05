"""
Kaydırak - 2 Günlük (48 Saatlik) Ana Havuz (1.330 Ürün) Otomatik Tazeleme Motoru
Her 48 saatte bir Amazon TR, Hepsiburada ve Idefix'in 32 alt kategorisindeki Çok Satanlar
listelerini tarar, güncel mağaza fiyatlarını (Idefix thirtyDaysLowPrice dahil) çeker,
tüm görselleri HTTP 200 ile doğrular ve backend/pool/*.json dosyalarını günceller.
"""

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
    SUBCATEGORIES,
    clean_title,
    is_valid_for_category,
    compute_prices,
    parse_tr_price,
    verify_pool_images,
    harvest_hepsiburada,
)

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

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

urllib3.disable_warnings()


def harvest_amazon_with_warmup():
    print("\n=== [2-DAY POOL REFRESH] HARVESTING AMAZON TR (32 Sub-Categories) ===")
    pool = {cat: [] for cat in SUBCATEGORIES}
    seen_asins = set()
    seen_titles = set()
    session = cffi_requests.Session()
    headers = {
        'Accept-Language': 'tr-TR,tr;q=0.9',
        'Referer': 'https://www.amazon.com.tr/',
    }
    try:
        session.get(
            'https://www.amazon.com.tr/',
            impersonate='chrome120',
            headers=headers,
            timeout=10,
            verify=False,
        )
    except Exception:
        pass

    for cat, subcats in SUBCATEGORIES.items():
        for subcat_name, queries in subcats:
            subcat_count = 0
            for q in queries:
                if subcat_count >= 14:
                    break
                url = f"https://www.amazon.com.tr/s?k={std_requests.utils.quote(q)}&s=exact-aware-popularity-rank"
                try:
                    cards = []
                    for _ in range(2):
                        r = session.get(
                            url,
                            impersonate='chrome120',
                            headers=headers,
                            timeout=10,
                            verify=False,
                        )
                        if r.status_code == 200:
                            soup = BeautifulSoup(r.text, 'html.parser')
                            cards = soup.select('div.s-result-item[data-asin]')
                            if len(cards) > 4:
                                break
                        time.sleep(0.4)

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
                        if (
                            not img_url.startswith('https://m.media-amazon.com/images/I/')
                            or not img_url.endswith('.jpg')
                            or '.js' in img_url
                        ):
                            continue
                        img_url = re.sub(r'\._AC_[^.]+_\.jpg$', '._AC_UL500_.jpg', img_url)
                        title = clean_title(img_el.get('alt') or '')
                        if not is_valid_for_category(title, cat):
                            continue
                        title_key = title.lower()[:45]
                        if title_key in seen_titles:
                            continue
                        price_el = card.select_one(
                            'span.a-price:not([data-a-strike]) span.a-offscreen'
                        )
                        if not price_el:
                            continue
                        sale_val = parse_tr_price(price_el.get_text())
                        old_el = card.select_one(
                            'span.a-price[data-a-strike] span.a-offscreen'
                        )
                        orig_val = parse_tr_price(old_el.get_text()) if old_el else 0.0
                        orig, disc, rate = compute_prices(orig_val, sale_val, asin)
                        if not orig:
                            continue
                        seen_asins.add(asin)
                        seen_titles.add(title_key)
                        subcat_count += 1
                        pool[cat].append({
                            'id': f'amz-{asin}',
                            'title': title,
                            'originalPrice': orig,
                            'discountedPrice': disc,
                            'discountRate': rate,
                            'imageUrl': img_url,
                            'productUrl': f'https://www.amazon.com.tr/dp/{asin}',
                            'store': 'Amazon TR',
                            'category': cat,
                            'subCategory': subcat_name,
                        })
                    time.sleep(0.2)
                except Exception as e:
                    print(f"  [Amazon TR Error] {q}: {e}")
    return pool


def harvest_idefix_exact():
    print("\n=== [2-DAY POOL REFRESH] HARVESTING IDEFIX (32 Sub-Categories) ===")
    idf_pool = {cat: [] for cat in SUBCATEGORIES}
    seen_idf_ids = set()
    seen_idf_titles = set()
    idf_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'tr-TR,tr;q=0.9',
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
                    items = (
                        (pp.get('categoryData') or {}).get('items')
                        or (pp.get('landingData') or {}).get('items')
                        or []
                    )
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
                        orig_val = max(
                            float(v.get('price') or 0),
                            float(v.get('thirtyDaysLowPrice') or 0),
                        )
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
                            'subCategory': subcat_name,
                        })
                    time.sleep(0.15)
                except Exception as e:
                    print(f"  [Idefix Error] {p_url}: {e}")
    return idf_pool


def merge_and_save_pool(fresh_pool, filename, store_label, target_per_cat=112):
    path = os.path.join('backend', 'pool', filename)
    existing_pool = {cat: [] for cat in SUBCATEGORIES}
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                existing_pool = json.load(f)
        except Exception:
            pass

    merged_pool = {cat: [] for cat in SUBCATEGORIES}
    for cat in SUBCATEGORIES:
        fresh_items = fresh_pool.get(cat, [])
        old_items = existing_pool.get(cat, [])
        fresh_by_id = {it['id']: it for it in fresh_items}

        combined = list(fresh_items)
        seen_ids = {it['id'] for it in combined}
        seen_titles = {it['title'].lower()[:45] for it in combined}

        for old_it in old_items:
            if old_it['id'] in fresh_by_id:
                continue
            if old_it['id'] not in seen_ids and old_it['title'].lower()[:45] not in seen_titles:
                combined.append(old_it)
                seen_ids.add(old_it['id'])
                seen_titles.add(old_it['title'].lower()[:45])

        merged_pool[cat] = combined[: target_per_cat + 15]

    verified_pool = verify_pool_images(merged_pool, store_label)
    for cat in SUBCATEGORIES:
        verified_pool[cat] = verified_pool[cat][:target_per_cat]

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(verified_pool, f, ensure_ascii=False, indent=2)

    counts = {cat: len(verified_pool[cat]) for cat in SUBCATEGORIES}
    print(f"Saved {filename}: {counts} (Total: {sum(counts.values())})")


def refresh_all_master_pools():
    print("\n========================================================")
    print("  STARTING 48-HOUR (2-DAY) MASTER POOL REFRESH (1,330)")
    print("========================================================")
    try:
        amz_fresh = harvest_amazon_with_warmup()
        merge_and_save_pool(amz_fresh, 'pool_amazon.json', 'Amazon TR')
    except Exception as e:
        print(f"Amazon TR pool refresh warning: {e}")

    try:
        hb_fresh = harvest_hepsiburada()
        merge_and_save_pool(hb_fresh, 'pool_hepsiburada.json', 'Hepsiburada')
    except Exception as e:
        print(f"Hepsiburada pool refresh warning: {e}")

    try:
        idf_fresh = harvest_idefix_exact()
        merge_and_save_pool(idf_fresh, 'pool_idefix.json', 'Idefix')
    except Exception as e:
        print(f"Idefix pool refresh warning: {e}")

    print("========================================================")
    print("  48-HOUR MASTER POOL REFRESH COMPLETED SUCCESSFULLY")
    print("========================================================\n")


if __name__ == '__main__':
    refresh_all_master_pools()
