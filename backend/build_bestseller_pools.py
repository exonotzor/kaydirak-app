import json
import os
import re
import sys
import time
import html
import hashlib
import urllib3
import requests as std_requests
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

urllib3.disable_warnings()

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(PROJECT_DIR)

# 32 Sub-Categories (8 per Main Category)
SUBCATEGORIES = {
    'Teknoloji': [
        ('Projeksiyon & Ev Sineması', ['mini projeksiyon cihazı', 'android tv box', 'taşınabilir projeksiyon']),
        ('Oyun & Konsol', ['el oyun konsolu', 'oyuncu gamepad', 'direksiyon seti', 'vr sanal gerçeklik gözlüğü']),
        ('Akıllı Ev & Otomasyon', ['akıllı priz wifi', 'akıllı led şerit', 'akıllı ev güvenlik kamerası']),
        ('Tablet & Çizim', ['android tablet', 'grafik çizim tableti', 'e-kitap okuyucu']),
        ('Monitör & Ekran', ['oyuncu monitörü', 'taşınabilir monitör', 'monitör standı kolu']),
        ('3D & Maker', ['3d yazıcı kalem', 'dijital mikroskop', 'lehim havya seti']),
        ('Drone & Aksiyon', ['kameralı drone', 'aksiyon kamerası', 'telefon gimbal sabitleyici']),
        ('Mekanik Klavye', ['mekanik klavye', 'kablosuz klavye', 'rgb büyük mouse pad']),
        ('Kulaklık & Ses', ['anc bluetooth kulaklık', 'oyuncu kulaklığı', 'kulak içi tws kulaklık']),
        ('Veri Depolama & SSD', ['taşınabilir ssd 1tb', 'nvme m2 ssd', 'micro sd kart 256gb']),
        ('Enerji & Güç', ['powerbank 20000mah hızlı şarj', 'akım korumalı priz usb', 'gan hızlı şarj adaptörü']),
        ('Ağ & Wi-Fi', ['wifi 6 router', 'mesh wifi sistemi', 'wifi menzil genişletici']),
        ('Fotoğraf & Video', ['şipşak fotoğraf makinesi', 'ring light led halka ışık', 'kablosuz yaka mikrofonu']),
        ('Oto Teknolojisi', ['araç içi kamera', 'şarjlı lastik şişirme pompası', 'fm transmitter bluetooth']),
        ('Ofis & Etiket', ['mini termal etiket yazıcı', 'usb c çoklayıcı hub', 'soğutucu laptop standı']),
        ('Mouse & Akıllı Saat & Ses', ['kablosuz mouse', 'akıllı saat', 'bluetooth hoparlör', 'usb webcam'])
    ],
    'Moda': [
        ('Erkek Üst Giyim', ['erkek tişört', 'erkek gömlek', 'erkek sweatshirt']),
        ('Kadın Giyim', ['kadın elbise', 'kadın bluz', 'kadın triko kazak']),
        ('Dış Giyim', ['erkek ceket', 'kadın trençkot', 'erkek şişme mont']),
        ('Jean & Pantolon', ['erkek jean pantolon', 'kadın mom jean', 'erkek eşofman altı']),
        ('Çanta & Valiz', ['sırt çantası', 'kadın omuz çantası', 'kabin boy valiz']),
        ('Saat & Gözlük', ['güneş gözlüğü', 'erkek kol saati', 'kadın kol saati']),
        ('Takı & Aksesuar', ['gümüş kolye kadın', 'erkek deri kemer', 'erkek deri cüzdan']),
        ('Ev Giyimi & Pijama', ['kadın pijama takımı', 'erkek pijama takımı', 'polar sabahlık']),
        ('Spor & Aktif Giyim', ['kadın spor tayt', 'erkek spor şort', 'eşofman takımı']),
        ('Şapka & Atkı', ['beyzbol şapka', 'kaşmir atkı bere', 'deri eldiven']),
        ('Seyahat Düzenleyici', ['makyaj çantası', 'seyahat düzenleyici set', 'kartlık cüzdan']),
        ('Ayakkabı & Sneaker', ['erkek sneaker', 'kadın spor ayakkabı', 'deri bot'])
    ],
    'Ev & Yaşam': [
        ('Küçük Ev Aletleri', ['airfryer fritöz', 'blender seti', 'tost makinesi']),
        ('Pişirme & Tencere', ['çelik tencere seti', 'döküm tava', 'fırın tepsisi borcam']),
        ('Sofra & Sunum', ['yemek takımı 24 parça', 'şef bıçağı seti', 'bambu sunum tahtası']),
        ('Ev Tekstili', ['pamuk nevresim takımı', 'banyo havlu seti', 'ortopedik visco yastık']),
        ('Ütü & Süpürge', ['buharlı ütü', 'dikey şarjlı süpürge', 'robot süpürge']),
        ('Aydınlatma & Dekor', ['şarjlı masa lambası', 'dekoratif duvar saati', 'kokulu mum difüzör']),
        ('Düzenleyici & Depolama', ['dolap içi düzenleyici', 'vakumlu hurç seti', 'cam saklama kabı']),
        ('Tamir & Hırdavat', ['şarjlı vidalama matkap', 'takım çantası seti', 'lazer metre']),
        ('Kamp & Outdoor', ['kamp sandalyesi', 'kamp çadırı', 'şarjlı kamp feneri']),
        ('Spor & Ev Fitness', ['pilates matı', 'ayarlanabilir dambıl seti', 'atlama ipi sayacı']),
        ('Kutu Oyunu & Hobi', ['kutu oyunu aile', '1000 parça puzzle', 'ahşap satranç takımı']),
        ('Banyo & Temizlik', ['tablet mop temizlik seti', 'banyo paspas takımı', 'çamaşır kurutmalık']),
        ('Bitki & Balkon', ['seramik saksı seti', 'bahçe sulama tabancası', 'solar bahçe aydınlatma']),
        ('Kahve & Termos', ['filtre kahve makinesi', 'çelik termos', 'türk kahvesi makinesi'])
    ],
    'Kozmetik': [
        ('Parfüm & Deodorant', ['erkek parfüm edp', 'kadın parfüm edp', 'vücut spreyi mist']),
        ('Cilt Serumu & Asit', ['c vitamini serum', 'hyaluronik asit serum', 'niacinamide serum']),
        ('Yüz Bakımı & Maske', ['yüz nemlendirici krem', 'kil maskesi yüz', 'kağıt yüz maskesi']),
        ('Kore Kozmetik & Tonik', ['kore cilt bakım', 'glikolik asit tonik', 'yüz temizleme köpüğü']),
        ('Güneş Bakımı', ['güneş kremi spf 50', 'leke karşıtı güneş kremi']),
        ('Saç Bakımı', ['keratin şampuan', 'saç bakım yağı', 'saç maskesi']),
        ('Makyaj & Göz', ['maskara', 'far paleti', 'eyeliner suya dayanıklı']),
        ('Dudak & Tırnak', ['likit mat ruj', 'dudak nemlendirici balm', 'kalıcı oje seti']),
        ('Kişisel Bakım Cihazı', ['tıraş makinesi', 'saç kurutma makinesi', 'saç düzleştirici']),
        ('Ağız & Diş Bakımı', ['şarjlı diş fırçası', 'beyazlatıcı diş macunu', 'ağız duşu']),
        ('Erkek Bakım & Sakal', ['sakal bakım yağı', 'tıraş sonrası losyon', 'saç şekillendirici wax']),
        ('Vücut & Aromaterapi', ['vücut losyonu', 'vücut peeling scrub', 'masaj yağı aromaterapi'])
    ]
}

# Dart DealItem.sanitizeCategory keywords + strict noise filters for Teknoloji
DART_NON_TECH_KEYWORDS = [
    'krem', 'serum', 'losyon', 'nemlendirici', 'hydro boost', 'nivea',
    'neutrogena', 'loreal', 'parfüm', 'parfum', 'deodorant', 'şampuan', 'sampuan',
    'maske', 'makyaj', 'ruj', 'rimel', 'maskara', 'cilt', 'bakım yağı', 'tonik',
    'güneş kremi', 'skinmaster', 'yüz temizleme', 'dudak', 'kolonya',
    'yelek', 'mont', 'şort', 'sort', 'kapri', 'pantolon', 't-shirt',
    'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı',
    'bot', 'çorap', 'ceket', 'gömlek', 'polar', 'tayt', 'içlik',
    'boxer', 'kaban', 'atlet', 'elbise', 'etek', 'buzluk', 'cooler'
]

# Extra filter to keep Teknoloji free of phone cases, cables, chargers, batteries
TECH_ACCESSORY_BAN = [
    'kılıf', 'kilif', 'ekran koruyucu', 'temperli', 'cam koruyucu', 'kamera koruyucu',
    'kalem pil', 'ince pil', 'aaa pil', 'aa pil', 'şarjlı pil', 'pil şarj',
    'şarj aleti', 'şarj cihazı', 'şarj adaptörü', 'duvar şarj', 'hızlı şarj',
    'type-c kablo', 'type c kablo', 'şarj kablosu', 'data kablosu', 'lightning kablo',
    'kordon', 'kayış', 'kolye', 'yüzük', 'temizleme kiti', 'sticker', 'çanta', 'çantası'
]

# Filter spare parts / cleaning tablets from Ev & Yaşam
HOME_SPARE_BAN = [
    'kireç çözücü', 'bakım paketi', 'temizleme tableti', 'yedek parça',
    'toz torbası', 'filtre kağıdı', 'su filtresi', 'yedek başlık', 'kılıfı'
]

def clean_title(raw_title):
    if not raw_title:
        return ''
    t = html.unescape(str(raw_title)).strip()
    t = re.sub(r'^Sponsorlu\s+reklam\s*[-–—:]\s*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def is_valid_for_category(title, category):
    tl = title.lower()
    if len(title) < 8:
        return False
    if category == 'Teknoloji':
        if any(kw in tl for kw in DART_NON_TECH_KEYWORDS):
            return False
        if any(kw in tl for kw in TECH_ACCESSORY_BAN):
            return False
    elif category == 'Ev & Yaşam':
        if any(kw in tl for kw in HOME_SPARE_BAN):
            return False
    return True

def compute_prices(orig_price, sale_price, unique_key):
    """
    Ensures originalPrice > discountedPrice > 0 for APK compatibility,
    without requiring high discounts. Uses real discount if >= 5%,
    otherwise sets a modest reference list price (+10% to +18%).
    """
    if sale_price <= 25 or sale_price > 65000:
        return None, None, None
    h = int(hashlib.md5(unique_key.encode('utf-8')).hexdigest()[:4], 16)
    fallback_rate = 10 + (h % 9)  # 10% to 18%
    if orig_price and orig_price > sale_price:
        rate = round(((orig_price - sale_price) / orig_price) * 100)
        if 5 <= rate <= 75:
            return round(orig_price, 2), round(sale_price, 2), int(rate)
    orig = float(round(sale_price / (1.0 - fallback_rate / 100.0)))
    if orig <= sale_price:
        orig = float(int(sale_price) + 10)
    actual_rate = max(5, int(round(((orig - sale_price) / orig) * 100)))
    return orig, round(sale_price, 2), actual_rate

def parse_tr_price(text):
    if not text:
        return 0.0
    m = re.search(r'((?:\d{1,3}\.)*\d+(?:,\d{1,2})?)', str(text))
    if not m:
        return 0.0
    val_str = m.group(1).replace('.', '').replace(',', '.')
    try:
        return float(val_str)
    except Exception:
        return 0.0

# 1. AMAZON TR HARVESTER (Best Sellers Sort + Strict Container Parsing)
def harvest_amazon():
    print("\n=== 1. HARVESTING AMAZON TR (Best Sellers & 32 Sub-Categories) ===")
    pool = {cat: [] for cat in SUBCATEGORIES}
    seen_asins = set()
    seen_titles = set()
    session = cffi_requests.Session()
    headers = {'Accept-Language': 'tr-TR,tr;q=0.9'}

    for cat, subcats in SUBCATEGORIES.items():
        for subcat_name, queries in subcats:
            subcat_count = 0
            for q in queries:
                if subcat_count >= 14:
                    break
                # Sort by exact-aware-popularity-rank (Amazon Best Sellers order)
                url = f"https://www.amazon.com.tr/s?k={std_requests.utils.quote(q)}&s=exact-aware-popularity-rank"
                try:
                    r = session.get(url, impersonate='chrome120', headers=headers, timeout=10, verify=False)
                    if r.status_code != 200:
                        continue
                    soup = BeautifulSoup(r.text, 'html.parser')
                    cards = soup.select('div.s-result-item[data-asin]')
                    for card in cards:
                        if subcat_count >= 14:
                            break
                        asin = (card.get('data-asin') or '').strip()
                        if len(asin) != 10 or not asin.startswith('B0') or asin in seen_asins:
                            continue
                        # Skip sponsored ads to avoid unrelated category ads
                        if 'Sponsorlu' in card.get_text():
                            continue
                        img_el = card.select_one('img.s-image')
                        if not img_el:
                            continue
                        img_url = (img_el.get('src') or '').strip()
                        if not img_url.startswith('https://m.media-amazon.com/images/I/') or not img_url.endswith('.jpg') or '.js' in img_url:
                            continue
                        # Upgrade thumbnail resolution cleanly to _AC_UL500_.jpg
                        img_url = re.sub(r'\._AC_[^.]+_\.jpg$', '._AC_UL500_.jpg', img_url)

                        # Title directly from the same card's h2 or img alt
                        title = clean_title(img_el.get('alt') or '')
                        if not title:
                            h2 = card.select_one('h2')
                            title = clean_title(h2.get_text() if h2 else '')
                        if not is_valid_for_category(title, cat):
                            continue
                        if title.lower()[:45] in seen_titles:
                            continue

                        # Price strictly from the same card container
                        price_el = card.select_one('span.a-price:not([data-a-strike]) span.a-offscreen')
                        if not price_el:
                            whole = card.select_one('span.a-price:not([data-a-strike]) span.a-price-whole')
                            frac = card.select_one('span.a-price:not([data-a-strike]) span.a-price-fraction')
                            if whole:
                                p_txt = f"{whole.get_text().strip()},{frac.get_text().strip() if frac else '00'}"
                                sale_val = parse_tr_price(p_txt)
                            else:
                                continue
                        else:
                            sale_val = parse_tr_price(price_el.get_text())

                        old_el = card.select_one('span.a-price[data-a-strike] span.a-offscreen')
                        orig_val = parse_tr_price(old_el.get_text()) if old_el else 0.0

                        orig, disc, rate = compute_prices(orig_val, sale_val, asin)
                        if not orig:
                            continue

                        seen_asins.add(asin)
                        seen_titles.add(title.lower()[:45])
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
                            'subCategory': subcat_name
                        })
                    time.sleep(0.25)
                except Exception as e:
                    print(f"  [AMZ Error] {q}: {e}")
            print(f"  [Amazon TR] {cat} -> {subcat_name}: +{subcat_count} items (Total {cat}: {len(pool[cat])})")
    return pool

# 2. HEPSIBURADA HARVESTER (Best Sellers Sort + Structured JSON Parsing)
def harvest_hepsiburada(per_subcat=32):
    print(f"\n=== 2. HARVESTING HEPSIBURADA (Best Sellers & 32 Sub-Categories, target {per_subcat}/subcat) ===")
    pool = {cat: [] for cat in SUBCATEGORIES}
    seen_ids = set()
    seen_titles = set()
    headers = {'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)'}

    for cat, subcats in SUBCATEGORIES.items():
        target_for_cat = 18 if cat == 'Teknoloji' else (20 if cat in ('Ev & Yaşam', 'Moda', 'Kozmetik') else per_subcat)
        for subcat_name, queries in subcats:
            if subcat_name == 'Mouse & Akıllı Saat & Ses':
                subcat_cap = 12
            elif subcat_name in ('Ayakkabı & Sneaker', 'Kahve & Termos'):
                subcat_cap = 22
            else:
                subcat_cap = target_for_cat
            subcat_count = 0
            for q in queries:
                if subcat_count >= subcat_cap:
                    break
                url = f"https://www.hepsiburada.com/ara?q={std_requests.utils.quote(q)}&siralama=coksatan"
                try:
                    r = std_requests.get(url, headers=headers, verify=False, timeout=8)
                    if r.status_code != 200:
                        continue
                    scripts = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)
                    for s in scripts:
                        sc = s.strip()
                        if sc.startswith('{') and 'productStat' in sc:
                            data = json.loads(sc)
                            prods = data.get('searchState', {}).get('searchProductArray', [])
                            for p in prods:
                                if subcat_count >= subcat_cap:
                                    break
                                pid = str(p.get('productId') or '').strip()
                                title = clean_title(p.get('name') or '')
                                if not pid or pid in seen_ids or not is_valid_for_category(title, cat):
                                    continue
                                if title.lower()[:45] in seen_titles:
                                    continue

                                prod_url = (p.get('productUrl') or '').strip()
                                if not prod_url:
                                    continue
                                if not prod_url.startswith('http'):
                                    prod_url = 'https://www.hepsiburada.com' + prod_url

                                imgs = p.get('images') or []
                                if not imgs:
                                    continue
                                img_url = (imgs[0].get('linkFormat') or '').replace('{size}', '550').strip()
                                if not img_url.startswith('https://') or not img_url.endswith('.jpg'):
                                    continue

                                pa = p.get('priceArea', {}).get('priceInfo', {})
                                tp = (pa.get('topPrice') or {}).get('value')
                                bp = (pa.get('bottomPrice') or {}).get('value')
                                sale_val = float(bp or tp or 0)
                                orig_val = float(tp or 0) if (tp and bp and float(tp) > float(bp)) else 0.0

                                orig, disc, rate = compute_prices(orig_val, sale_val, pid)
                                if not orig:
                                    continue

                                seen_ids.add(pid)
                                seen_titles.add(title.lower()[:45])
                                subcat_count += 1
                                pool[cat].append({
                                    'id': f'hb-{pid}',
                                    'title': title,
                                    'originalPrice': orig,
                                    'discountedPrice': disc,
                                    'discountRate': rate,
                                    'imageUrl': img_url,
                                    'productUrl': prod_url,
                                    'store': 'Hepsiburada',
                                    'category': cat,
                                    'subCategory': subcat_name
                                })
                            break
                    time.sleep(0.2)
                except Exception as e:
                    print(f"  [HB Error] {q}: {e}")
            print(f"  [Hepsiburada] {cat} -> {subcat_name}: +{subcat_count} items (Total {cat}: {len(pool[cat])})")
    return pool

# 3. IDEFIX HARVESTER (Structured __NEXT_DATA__ JSON Parsing)
def harvest_idefix():
    print("\n=== 3. HARVESTING IDEFIX (Popular Products & 32 Sub-Categories) ===")
    pool = {cat: [] for cat in SUBCATEGORIES}
    seen_ids = set()
    seen_titles = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'tr-TR,tr;q=0.9'
    }

    for cat, subcats in SUBCATEGORIES.items():
        for subcat_name, queries in subcats:
            subcat_count = 0
            for q in queries:
                if subcat_count >= 14:
                    break
                url = f"https://www.idefix.com/search?q={std_requests.utils.quote(q)}&sayfa=1"
                try:
                    r = std_requests.get(url, headers=headers, verify=False, timeout=8)
                    if r.status_code != 200 or '__NEXT_DATA__' not in r.text:
                        continue
                    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.DOTALL)
                    if not m:
                        continue
                    d = json.loads(m.group(1))
                    items = d.get('props', {}).get('pageProps', {}).get('searchData', {}).get('items', [])
                    for it in items:
                        if subcat_count >= 14:
                            break
                        variants = it.get('variants') or [it]
                        v = variants[0]
                        vid = str(v.get('id') or it.get('id') or '').strip()
                        title = clean_title(v.get('name') or it.get('name') or '')
                        if not vid or vid in seen_ids or not is_valid_for_category(title, cat):
                            continue
                        if title.lower()[:45] in seen_titles:
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

                        orig_val = float(v.get('price') or 0)
                        sale_val = float(v.get('discountedSalesPrice') or orig_val or 0)

                        orig, disc, rate = compute_prices(orig_val, sale_val, vid)
                        if not orig:
                            continue

                        seen_ids.add(vid)
                        seen_titles.add(title.lower()[:45])
                        subcat_count += 1
                        pool[cat].append({
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
                    print(f"  [Idefix Error] {q}: {e}")
            print(f"  [Idefix] {cat} -> {subcat_name}: +{subcat_count} items (Total {cat}: {len(pool[cat])})")
    return pool

# 4. LIVE HTTP 200 IMAGE VERIFIER
def verify_pool_images(pool, store_label):
    all_items = [it for cat_items in pool.values() for it in cat_items]
    print(f"\nVerifying {len(all_items)} image URLs for {store_label} via live HTTP 200 check...")

    def check_one(item):
        url = item['imageUrl']
        try:
            r = std_requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=6, verify=False, stream=True)
            ct = (r.headers.get('Content-Type') or '').lower()
            ok = (r.status_code == 200 and 'image' in ct)
            r.close()
            return item, ok
        except Exception:
            return item, False

    verified_pool = {cat: [] for cat in SUBCATEGORIES}
    broken_count = 0
    with ThreadPoolExecutor(max_workers=25) as ex:
        futures = [ex.submit(check_one, it) for it in all_items]
        for fut in as_completed(futures):
            it, ok = fut.result()
            if ok:
                verified_pool[it['category']].append(it)
            else:
                broken_count += 1

    print(f"  [{store_label}] Verified OK: {sum(len(v) for v in verified_pool.values())}, Dropped broken images: {broken_count}")
    return verified_pool

if __name__ == '__main__':
    os.makedirs(os.path.join('backend', 'pool'), exist_ok=True)

    amz_pool = harvest_amazon()
    amz_pool = verify_pool_images(amz_pool, 'Amazon TR')
    with open('backend/pool/pool_amazon.json', 'w', encoding='utf-8') as f:
        json.dump(amz_pool, f, ensure_ascii=False, indent=2)

    hb_pool = harvest_hepsiburada()
    hb_pool = verify_pool_images(hb_pool, 'Hepsiburada')
    with open('backend/pool/pool_hepsiburada.json', 'w', encoding='utf-8') as f:
        json.dump(hb_pool, f, ensure_ascii=False, indent=2)

    idf_pool = harvest_idefix()
    idf_pool = verify_pool_images(idf_pool, 'Idefix')
    with open('backend/pool/pool_idefix.json', 'w', encoding='utf-8') as f:
        json.dump(idf_pool, f, ensure_ascii=False, indent=2)

    # Reset rotation_state.json so no legacy IDs remain
    with open('backend/rotation_state.json', 'w', encoding='utf-8') as f:
        json.dump({
            'rotation_count': 0,
            'last_rotation_timestamp': None,
            'history': []
        }, f, ensure_ascii=False, indent=2)

    print("\n================ FINAL POOL SUMMARY ================")
    for name, p in [('Amazon TR', amz_pool), ('Hepsiburada', hb_pool), ('Idefix', idf_pool)]:
        counts = {c: len(p[c]) for c in SUBCATEGORIES}
        print(f"  {name:15}: {counts} (Total: {sum(counts.values())})")
