import json, re
from collections import defaultdict, Counter

def normalize_text(text):
    t = text.lower()
    t = t.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
    t = re.sub(r'[^\w\s]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def classify_deal(title, source_cat=""):
    n = normalize_text(title)
    
    # Check clothing color "krem" (e.g. krem kazak, krem ceket, krem mont, krem rengi)
    is_cream_color = bool(re.search(r'\bkrem\s+(kazak|hirka|ceket|mont|triko|pantolon|gomlek|polo|blazer|renk|renkli)\b', n) or 
                          re.search(r'\b(kazak|hirka|ceket|mont|triko|pantolon|gomlek|polo|blazer)\b.*\bkrem\b', n))

    # 1. TEKNOLOJI
    # Real electronics, gadgets, computer, mobile, audio, watches, health tech
    tech_patterns = [
        r'\bkulakl(i|ı)k\b', r'\btws\b', r'\bheadphone\b', r'\bearphone\b', r'\bairdots\b', r'\bearbuds\b',
        r'\bmouse\b', r'\bfare\b', r'\bklavye\b', r'\bkeyboard\b',
        r'\bhoparl(o|ö)r\b', r'\bspeaker\b', r'\bsoundbar\b',
        r'\bpowerbank\b', r'\btasinabilir sarj\b',
        r'\b(s|ş)arj\b', r'\badapt(o|ö)r\b', r'\bkablo\b', r'\btype\s*c\b', r'\blightning\b', r'\busb\b',
        r'\bak(i|ı)ll(i|ı)\s*saat\b', r'\bsmart\s*watch\b', r'\bkol\s*saati\b', r'\bak(i|ı)ll(i|ı)\s*bileklik\b', r'\bsmart\s*band\b',
        r'\bwatch\b', r'\bcasio\b', r'\bedifice\b', r'\bspovan\b',
        r'\bwebcam\b', r'\bkamera\b', r'\bcamera\b',
        r'\bmonit(o|ö)r\b', r'\bmonitor\b',
        r'\bpil\b', r'\bbattery\b',
        r'\bt(i|ı)ra(s|ş)\s*makinesi\b', r'\bko(s|ş)u\s*band(i|ı)\b', r'\bgaming\b', r'\bbluetooth\b'
    ]
    # Guard against false tech (e.g., "48 saat nemlendirme", "su gecirmez yelek", "camasir")
    has_tech_kw = any(re.search(p, n) for pts in [tech_patterns] for p in pts)
    if '48 saat' in n or '24 saat' in n or '72 saat' in n:
        # If "saat" only came from duration like "48 saat nemlendirme", don't count it as tech watch
        temp_n = re.sub(r'\b\d+\s*saat\b', ' ', n)
        has_tech_kw = any(re.search(p, temp_n) for p in tech_patterns)
    
    # 2. KOZMETIK
    cosmetic_patterns = [
        r'\bkrem\b', r'\bcream\b', r'\bserum\b', r'\blosyon\b', r'\blotion\b', r'\bnemlendirici\b',
        r'\bparf(u|ü)m\b', r'\bedp\b', r'\bedt\b', r'\b(s|ş)ampuan\b', r'\bshampoo\b',
        r'\bruj\b', r'\blipstick\b', r'\bmaskara\b', r'\bmascara\b', r'\brimel\b',
        r'\bcilt\s*bak(i|ı)m(i|ı)\b', r'\bg(u|ü)ne(s|ş)\s*kremi\b', r'\bg(u|ü)ne(s|ş)\s*spreyi\b',
        r'\bsun\s*screen\b', r'\bspf\b', r'\bkolajen\b', r'\bdi(s|ş)\s*macunu\b',
        r'\btonik\b', r'\bmicellar\b', r'\bv(u|ü)cut\s*s(u|ü)t(u|ü)\b', r'\bel\s*kremi\b', r'\by(u|ü)z\s*kremi\b',
        r'\bbb\s*krem\b', r'\bleke\s*kar(s|ş)(i|ı)t(i|ı)\b', r'\bk(i|ı)r(i|ı)(s|ş)(i|ı)kl(i|ı)k\b',
        r'\bsac\s*d(o|ö)k(u|ü)lmesi\b', r'\bag(i|ı)z\s*kokusu\b', r'\bdeodorant\b'
    ]
    cosmetic_brands = [
        'nivea', 'neutrogena', 'skinmaster', 'pureest', 'pure choice', 'juvera', 'lumene',
        'celenes', 'the purest', 'dermokil', 'erbatab', 'dkdent', 'golden rose', 'flormar',
        'tto', 'urban care', 'estee lauder', 'duru', 'bioderma', 'cerave', 'loreal', 'garnier'
    ]
    has_cosm_kw = (any(re.search(p, n) for p in cosmetic_patterns) and not is_cream_color) or any(re.search(r'\b' + b + r'\b', n) for b in cosmetic_brands)
    if 'slazenger' in n and any(w in n for w in ['parfum', 'toilette', 'deodarant', 'edt']):
        has_cosm_kw = True

    # 3. MODA
    apparel_patterns = [
        r'\bg(o|ö)mlek\b', r'\bpantolon\b', r'\bt[\s-]*shirt\b', r'\bti(s|ş)(o|ö)rt\b',
        r'\bsweatshirt\b', r'\bswet(s|ş)(o|ö)rt\b', r'\bkazak\b', r'\bh(i|ı)rka\b',
        r'\bceket\b', r'\bmont\b', r'\bkaban\b', r'\byelek\b', r'\bkapri\b', r'\b(s|ş)ort\b',
        r'\b(c|ç)orap\b', r'\bi(c|ç)lik\b', r'\bbot\b', r'\bsneaker\b', r'\bayakkab(i|ı)\b',
        r'\bterlik\b', r'\bsandalet\b', r'\b(c|ç)anta\b', r'\bs(i|ı)rt\s*(c|ç)antas(i|ı)\b',
        r'\btren(c|ç)kot\b', r'\btrenchcoat\b', r'\bpolar\b', r'\btayt\b', r'\be(s|ş)ofman\b',
        r'\belbise\b', r'\betek\b', r'\btriko\b', r'\bblazer\b', r'\bpolo\s*yaka\b',
        r'\bg(u|ü)ne(s|ş)\s*g(o|ö)zl(u|ü)g(u|ü)\b', r'\bg(o|ö)zl(u|ü)k\b', r'\bpants\b', r'\bhoodie\b'
    ]
    apparel_brands = [
        'us polo', 'u s polo', 'defacto', 'koton', 'benetton', 'columbia', 'calvin klein',
        'tommy jeans', 'tommy hilfiger', 'tommy life', 'only sons', 'only & sons', 'madmext',
        'merolife', 'mero life', 'pierre cardin', 'vess', 'loopa', 'muggo', 'head dexter',
        'millet', 'jack wolfskin', 'north face', 'ray ban', 'vogue'
    ]
    has_apparel_kw = any(re.search(p, n) for p in apparel_patterns) or any(re.search(r'\b' + b + r'\b', n) for b in apparel_brands)

    # 4. EV & YASAM
    home_patterns = [
        r'\btermos\b', r'\btencere\b', r'\btava\b', r'\bfincan\b', r'\bbardak\b', r'\bkupa\b',
        r'\btumbler\b', r'\bmatara\b', r'\bsahan\b', r'\bd(o|ö)k(u|ü)m\b', r'\bb(i|ı)(c|ç)ak\b',
        r'\bnevresim\b', r'\bpike\b', r'\b(c|ç)ar(s|ş)af\b', r'\byast(i|ı)k\b', r'\bhavlu\b',
        r'\bbornoz\b', r'\bsabun\b', r'\bdeterjan\b', r'\b(c|ç)ama(s|ş)(i|ı)r\b', r'\bbula(s|ş)(i|ı)k\b',
        r'\by(u|ü)zey\s*temizleyici\b', r'\bbuzluk\b', r'\bcooler\b', r'\bsaklama\s*kab(i|ı)\b',
        r'\bkavanoz\b', r'\bsu\s*p(i|ı)nar(i|ı)\b', r'\btemizleyici\b', r'\blamba\b', r'\bkesme\s*tahtas(i|ı)\b'
    ]
    home_brands = [
        'stanley', 'karaca', 'emsan', 'bonera', 'hascevher', 'korkmaz', 'english home',
        'madame coco', 'yatas', 'yataş', 'soley', 'nabaiji', 'ballarini', 'orret home',
        'siveno', 'incia', 'contigo', 'igloo', 'icepeak'
    ]
    has_home_kw = any(re.search(p, n) for p in home_patterns) or any(re.search(r'\b' + b + r'\b', n) for b in home_brands)

    # Priority Resolution:
    # 1. If it has cosmetic keywords/brands (Nivea, Neutrogena, serum, krem), it is Kozmetik!
    if has_cosm_kw and not has_home_kw and not has_apparel_kw:
        return 'Kozmetik'
    
    # 2. If it has cleaning detergents/soaps/termos/kitchen, it is Ev & Yaşam!
    if has_home_kw and not has_tech_kw and not has_apparel_kw:
        return 'Ev & Yaşam'

    # 3. If it has apparel keywords/brands, it is Moda!
    if has_apparel_kw and not has_tech_kw:
        return 'Moda'

    # 4. If it has real tech patterns:
    if has_tech_kw and not has_cosm_kw and not has_apparel_kw:
        return 'Teknoloji'

    # Disambiguation:
    if has_cosm_kw:
        return 'Kozmetik'
    if has_home_kw:
        return 'Ev & Yaşam'
    if has_apparel_kw:
        return 'Moda'
    if has_tech_kw:
        return 'Teknoloji'

    return source_cat if source_cat in ['Teknoloji', 'Moda', 'Ev & Yaşam', 'Kozmetik'] else 'Diğer'

if __name__ == '__main__':
    for fn in ['scraper/amazon_verified_deals.json', 'scraper/hepsiburada_verified_deals.json', 'scraper/idefix_strict_onpage.json', 'scraper/all_tech_verified.json']:
        try:
            with open(fn, 'r', encoding='utf-8') as f:
                data = json.load(f)
            counts = Counter(classify_deal(x['title'], x.get('category')) for x in data)
            print(f"{fn} ({len(data)} items): {dict(counts)}")
        except Exception as e:
            print(f"Error {fn}: {e}")
