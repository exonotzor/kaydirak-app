import json, re

def normalize_text(text):
    t = text.lower()
    t = t.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
    t = re.sub(r'[^\w\s]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def classify_product(title):
    n = normalize_text(title)
    
    # 1. KOZMETIK
    cosmetic_words = [
        'krem', 'cream', 'serum', 'losyon', 'lotion', 'nemlendirici', 'parfum', 'edp', 'edt',
        'sampuan', 'shampoo', 'ruj', 'lipstick', 'maskara', 'mascara', 'cilt bakimi',
        'gunes kremi', 'gunes spreyi', 'sun cream', 'sun sprey', 'spf', 'kolajen', 'dis macunu',
        'temizleme jeli', 'micellar', 'tonik', 'vucut sutu', 'el kremi', 'yuz kremi', 'bb krem',
        'leke karsiti', 'kirisiklik karsiti', 'agiz kokusu', 'goz cevresi', 'sac dokulmesi'
    ]
    cosmetic_brands = [
        'nivea', 'neutrogena', 'skinmaster', 'pureest', 'pure choice', 'juvera', 'lumene',
        'celenes', 'slazenger', 'alberto taccini', 'varens', 'lacoste essential', 'montblanc',
        'the purest', 'dermokil', 'erbatab', 'dkdent', 'golden rose', 'flormar', 'tto',
        'urban care', 'estee lauder', 'duru', 'bioderma', 'cerave'
    ]
    for w in cosmetic_words:
        if re.search(r'\b' + re.escape(w) + r'\b', n):
            return 'Kozmetik'
    for b in cosmetic_brands:
        if re.search(r'\b' + re.escape(b) + r'\b', n):
            if not any(cw in n for cw in ['sort', 'pantolon', 'tshirt', 'gomlek']):
                return 'Kozmetik'

    # 2. MODA
    apparel_words = [
        'gomlek', 'pantolon', 'tshirt', 'tisort', 't shirt', 'sweatshirt', 'swetsort',
        'kazak', 'hirka', 'ceket', 'mont', 'kaban', 'yelek', 'kapri', 'sort', 'corap',
        'iclik', 'bot', 'sneaker', 'ayakkabi', 'terlik', 'sandalet', 'canta', 'sirt cantasi',
        'trenckot', 'polar', 'tayt', 'esofman', 'elbise', 'etek', 'triko', 'blazer',
        'polo yaka', 'gunes gozlugu', 'gozluk', 'sunglasses', 'loose pants', 'swimsuit', 'mayo'
    ]
    apparel_brands = [
        'us polo', 'u s polo', 'defacto', 'koton', 'benetton', 'columbia', 'calvin klein',
        'tommy jeans', 'tommy hilfiger', 'tommy life', 'only sons', 'only & sons', 'madmext',
        'merolife', 'mero life', 'pierre cardin', 'vess', 'loopa', 'muggo', 'head dexter',
        'millet', 'jack wolfskin', 'north face', 'ray ban', 'vogue'
    ]
    for w in apparel_words:
        if re.search(r'\b' + re.escape(w) + r'\b', n):
            return 'Moda'
    for b in apparel_brands:
        if re.search(r'\b' + re.escape(b) + r'\b', n):
            return 'Moda'

    # 3. EV & YASAM
    home_words = [
        'termos', 'tencere', 'tava', 'fincan', 'bardak', 'kupa', 'tumbler', 'matara',
        'sahan', 'dokum', 'bicak', 'catal', 'kasik', 'nevresim', 'pike', 'carsaf',
        'yastik', 'havlu', 'bornoz', 'sabun', 'deterjan', 'camasir sabunu', 'bulasik sabunu',
        'yuzey temizleyici', 'buzluk', 'cooler', 'saklama kabi', 'kavanoz', 'su pinari',
        'camasir', 'bulasik', 'leke cikarici', 'biberon temizleyici', 'tencere seti'
    ]
    home_brands = [
        'stanley', 'karaca', 'emsan', 'bonera', 'hascevher', 'korkmaz', 'english home',
        'madame coco', 'yatas', 'soley', 'nabaiji', 'ballarini', 'orret home',
        'siveno', 'incia', 'contigo', 'igloo', 'icepeak'
    ]
    for w in home_words:
        if re.search(r'\b' + re.escape(w) + r'\b', n):
            return 'Ev & Yaşam'
    for b in home_brands:
        if re.search(r'\b' + re.escape(b) + r'\b', n):
            return 'Ev & Yaşam'

    # 4. TEKNOLOJI
    tech_words = [
        'kulaklik', 'tws', 'headphone', 'earphone', 'airdots', 'earbuds',
        'mouse', 'fare', 'klavye', 'keyboard', 'hoparlor', 'speaker', 'soundbar',
        'powerbank', 'sarj aleti', 'sarj', 'adaptor', 'kablo', 'type c', 'lightning',
        'akilli saat', 'smart watch', 'kol saati', 'akilli bileklik', 'smart band',
        'webcam', 'kamera', 'camera', 'monitor', 'ekran', 'pil', 'battery',
        'tiras makinesi', 'kosu bandi', 'edifice', 'spovan', 'gaming mouse'
    ]
    for w in tech_words:
        if re.search(r'\b' + re.escape(w) + r'\b', n):
            return 'Teknoloji'

    return 'Diğer'

if __name__ == '__main__':
    with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
        deals = json.load(f)

    print('Testing classification on current 120 deals:')
    changes = 0
    for i, d in enumerate(deals):
        old_cat = d.get('category')
        new_cat = classify_product(d.get('title'))
        if old_cat != new_cat:
            changes += 1
            t = d.get('title')[:55]
            print(f'[{i+1:3d}] MISMATCH: {t} -> Old: {old_cat} | New: {new_cat}')
    print(f'Total mismatches found: {changes}')
