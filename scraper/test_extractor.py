import json
import re
from collections import Counter

KNOWN_BRANDS = [
    # Top Priority Brands
    'stanley', 'xiaomi', 'redmi', 'apple', 'samsung', 'huawei', 'honor', 'lenovo', 'asus', 'hp', 'dell',
    'logitech', 'rampage', 'havit', 'razer', 'hyperx', 'steelseries', 'corsair',
    'anker', 'soundcore', 'spigen', 'baseus', 'ugreen', 'grundig', 'philips', 'jbl', 'sony',
    'tp-link', 'd-link', 'sandisk', 'kingston', 'casio', 'spovan',
    
    # Home & Kitchen
    'victorinox', 'karaca', 'tefal', 'korkmaz', 'hascevher', 'lava', 'nehir',
    'taç', 'tac', 'english home', 'madame coco', 'özdilek', 'ozdilek', 'yataş', 'yatas',
    'soley', 'mysoft', 'paşabahçe', 'pasabahce', 'borcam', 'schafer', 'arçelik', 'beko',
    'fakir', 'sinbo', 'decathlon', 'nabaiji',
    
    # Fashion / Shoes
    'adidas', 'nike', 'puma', 'under armour', 'columbia', 'skechers',
    'calvin klein', 'tommy jeans', 'tommy hilfiger', 'pierre cardin', 'only sons', 'only & sons', 'madmext',
    'u.s. polo', 'us polo', 'defacto', 'koton', 'avva', 'lufian', 'altınyıldız', 'altinyildiz',
    'kiğılı', 'kigili', 'beymen', 'network', 'vakko', 'benetton', 'jack & jones', 'jack jones',
    'alinda', 'vess', 'loopa', 'ixir', 'yiwu', 'mero life', 'muggo', 'onl', 'trendseninle',
    
    # Cosmetics & Personal Care
    'loreal', "l'oreal", 'garnier', 'nivea', 'maybelline', 'golden rose', 'flormar',
    'bioderma', 'la roche posay', 'la roche', 'cerave', 'neutrogena', 'procsin',
    'bargello', 'eyüp sabri', 'eyup sabri', 'duru', 'signal', 'colgate', 'sensodyne', 'oral-b',
    'arko', 'dalan', 'estee lauder', 'estee', 'tto', 'siveno', 'erbatab', 'urban care'
]

PRODUCT_TYPES = [
    # Tech types
    ('kulaklik', ['kulaklik', 'kulaklık', 'tws', 'headphone', 'earphone', 'airdots', 'earbuds']),
    ('mouse', ['mouse', 'fare']),
    ('klavye', ['klavye', 'keyboard']),
    ('powerbank', ['powerbank', 'power bank', 'tasinabilir sarj', 'taşınabilir şarj']),
    ('saat', ['saat', 'watch', 'smart band', 'akilli bileklik', 'akıllı bileklik']),
    ('hoparlor', ['hoparlor', 'hoparlör', 'speaker', 'soundbar']),
    ('sarj_aleti', ['sarj aleti', 'şarj aleti', 'adaptor', 'adaptör', 'charger']),
    ('kablo', ['kablo', 'cable', 'type-c to', 'usb to']),
    ('kamera', ['kamera', 'webcam', 'cam']),
    ('ssd', ['ssd', 'solid state']),
    ('usb_bellek', ['usb bellek', 'flash bellek']),
    ('pil', ['pil', 'battery', 'alkalin']),
    
    # Moda types
    ('mont', ['mont', 'kaban', 'parka', 'anorak']),
    ('ceket', ['ceket', 'blazer']),
    ('trenckot', ['trenckot', 'trençkot', 'trenchcoat']),
    ('hirka', ['hirka', 'hırka', 'cardigan']),
    ('kazak', ['kazak', 'triko', 'sweater', 'pullover']),
    ('sweatshirt', ['sweatshirt', 'hoodie']),
    ('polar', ['polar', 'fleece']),
    ('gomlek', ['gomlek', 'gömlek', 'shirt']),
    ('tshirt', ['tshirt', 'tişört', 't-shirt', 'atlet']),
    ('pantolon', ['pantolon', 'jean', 'denim', 'chino', 'tayt', 'legging']),
    ('esofman', ['esofman', 'eşofman', 'jogger', 'sweatpants']),
    ('ayakkabi', ['ayakkabi', 'ayakkabı', 'sneaker', 'spor ayakkabı', 'bot', 'çizme', 'cizme', 'terlik', 'sandalet']),
    ('canta', ['canta', 'çanta', 'backpack', 'sırt çantası', 'sirt cantasi', 'omuz cantasi', 'cüzdan', 'cuzdan']),
    
    # Ev & Yaşam types
    ('termos', ['termos', 'mug', 'matara', 'flask']),
    ('tencere', ['tencere', 'pot', 'döküm yayvan', 'gastro']),
    ('tava', ['tava', 'pan', 'sahan']),
    ('bicak', ['bicak', 'bıçak', 'soyacak', 'knife']),
    ('fincan', ['fincan', 'kahve seti', 'coffee cup']),
    ('bardak', ['bardak', 'kupa', 'tumbler', 'su takımı']),
    ('nevresim', ['nevresim', 'yatak örtüsü', 'pike']),
    ('havlu', ['havlu', 'towel', 'bornoz']),
    ('yastik', ['yastik', 'yastık', 'pillow', 'kırlent']),
    ('saklama_kabi', ['saklama kabi', 'saklama kabı', 'kavanoz', 'borcam']),
    
    # Kozmetik types
    ('parfum', ['parfum', 'parfüm', 'edp', 'edt', 'cologne', 'kolonya']),
    ('ruj', ['ruj', 'lipstick', 'lip gloss', 'dudak']),
    ('maskara', ['maskara', 'mascara', 'rimel']),
    ('krem', ['krem', 'cream', 'nemlendirici', 'lotion', 'losyon', 'balm']),
    ('serum', ['serum', 'ampul']),
    ('sampuan', ['sampuan', 'şampuan', 'shampoo', 'saç kremi']),
    ('temizleme', ['temizleme', 'micellar', 'tonik', 'yüz yıkama', 'jel']),
    ('gunes_kremi', ['gunes kremi', 'güneş kremi', 'sunscreen', 'spf']),
    ('dis_bakimi', ['dis macunu', 'diş macunu', 'dis fircasi', 'diş fırçası'])
]

def normalize_text(text):
    t = text.lower()
    t = t.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
    t = re.sub(r'[^\w\s]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def extract_brand_and_ptype(title):
    norm = normalize_text(title)
    
    # Check US Polo explicit SKU or terms
    if any(k in norm for k in ['polo', '50324708', '50324660', '5029688', 'vr079', 'vr016']):
        detected_brand = 'uspolo'
    else:
        detected_brand = None
        for b in KNOWN_BRANDS:
            b_norm = normalize_text(b)
            pattern = r'\b' + re.escape(b_norm) + r'\b'
            if re.search(pattern, norm):
                detected_brand = b_norm.replace(' ', '')
                break
                
        if not detected_brand:
            if norm.startswith('mavi') or 'mavi jeans' in norm:
                detected_brand = 'mavi'
            else:
                GENERIC_WORDS = {'erkek', 'kadin', 'cocuk', 'bebek', 'unisex', 'regular', 'slim', 'oversize', 'basic', 'yuksek', 'duz', 'cok', 'buyuk'}
                words = [w for w in norm.split() if w not in GENERIC_WORDS]
                detected_brand = words[0] if words else 'diger'

    detected_type = 'diger'
    for ptype, keywords in PRODUCT_TYPES:
        for kw in keywords:
            kw_norm = normalize_text(kw)
            if kw_norm in norm:
                detected_type = ptype
                break
        if detected_type != 'diger':
            break
            
    return detected_brand, detected_type

# Load HB
hb = json.load(open('scraper/hepsiburada_verified_deals.json', encoding='utf-8'))
print(f"Loaded {len(hb)} HB deals.")

hb_brand_types = Counter()
for x in hb:
    b, pt = extract_brand_and_ptype(x['title'])
    key = f"{b}_{pt}"
    hb_brand_types[key] += 1
    x['brand'] = b
    x['ptype'] = pt
    x['brand_type'] = key

print(f"Unique HB brand-types: {len(hb_brand_types)} out of {len(hb)}")
for k, cnt in hb_brand_types.most_common(10):
    print(f"  {k}: {cnt}")
