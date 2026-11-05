import json
from collections import Counter
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from test_extractor import extract_brand_and_ptype

def get_true_category(ptype, fallback_cat):
    if ptype in ['kulaklik', 'mouse', 'klavye', 'powerbank', 'saat', 'hoparlor', 'sarj_aleti', 'kablo', 'kamera', 'ssd', 'usb_bellek', 'pil']:
        return 'Teknoloji'
    if ptype in ['mont', 'ceket', 'kazak', 'hirka', 'polar', 'sweatshirt', 'gomlek', 'tshirt', 'pantolon', 'esofman', 'ayakkabi', 'canta', 'trenckot', 'yelek']:
        return 'Moda'
    if ptype in ['termos', 'tencere', 'tava', 'bicak', 'fincan', 'bardak', 'nevresim', 'havlu', 'yastik', 'saklama_kabi']:
        return 'Ev & Yaşam'
    if ptype in ['krem', 'serum', 'parfum', 'sampuan', 'ruj', 'maskara', 'temizleme', 'gunes_kremi', 'dis_bakimi', 'losyon']:
        return 'Kozmetik'
    return fallback_cat

with open('scraper/amazon_verified_deals.json', 'r', encoding='utf-8') as f:
    amz_pool = json.load(f)
with open('scraper/hepsiburada_verified_deals.json', 'r', encoding='utf-8') as f:
    hb_pool = json.load(f)
with open('scraper/idefix_strict_onpage.json', 'r', encoding='utf-8') as f:
    idf_strict = json.load(f)
with open('scraper/home_beauty_strict.json', 'r', encoding='utf-8') as f:
    idf_hb = json.load(f)
with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    idf_tech = json.load(f)

idf_pool = idf_strict + idf_hb + idf_tech

for pool, sname in [(amz_pool, 'Amazon TR'), (hb_pool, 'Hepsiburada'), (idf_pool, 'Idefix')]:
    for it in pool:
        it['store'] = sname
        b, pt = extract_brand_and_ptype(it['title'])
        it['brand'] = b
        it['ptype'] = pt
        it['brand_type'] = f"{b}_{pt}"
        it['category'] = get_true_category(pt, it.get('category', 'Diğer'))

print("AMZ by true cat:", Counter(x['category'] for x in amz_pool))
print("HB by true cat:", Counter(x['category'] for x in hb_pool))
print("IDF by true cat:", Counter(x['category'] for x in idf_pool))
