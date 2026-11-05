import json
from collections import Counter

with open('scraper/idefix_strict_onpage.json', 'r', encoding='utf-8') as f:
    idf_onpage = json.load(f)
with open('scraper/home_beauty_strict.json', 'r', encoding='utf-8') as f:
    idf_hb = json.load(f)
with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    idf_tech = json.load(f)

print(f"Idefix files: onpage={len(idf_onpage)}, hb={len(idf_hb)}, tech={len(idf_tech)}")

def extract_brand_and_type(title):
    t = title.lower()
    brand = 'diger'
    for b in ['casio', 'spovan', 'benetton', 'muggo', 'nehir', 'siveno', 'erbatab', 'head', 'tommy life', 'onltizana', 'mudo', 'pierre cardin', 'defacto', 'koton', 'lumberjack', 'us polo', 'u.s. polo']:
        if b in t:
            brand = b.replace(' ', '').replace('.', '')
            break
    if brand == 'diger':
        brand = t.split()[0] if t.split() else 'unknown'

    ptype = 'diger'
    for pt in ['saat', 'yuzuk', 'yüzük', 'kulaklik', 'kulaklık', 'bot', 'ayakkabi', 'ayakkabı', 'pantolon', 'sort', 'şort', 'kapri', 'gomlek', 'gömlek', 'kazak', 'tshirt', 'tişört', 'tayt', 'tava', 'tencere', 'sabun', 'deterjan', 'temizleyici', 'vitamin', 'serum', 'krem', 'roll on', 'deodorant']:
        if pt in t:
            ptype = pt.replace('ı', 'i').replace('ş', 's').replace('ç', 'c').replace('ö', 'o').replace('ü', 'u').replace('ğ', 'g')
            break
    return brand, ptype

# Test diversity on Idefix pool
all_idf_items = idf_onpage + idf_hb + idf_tech
diverse_idf = []
seen = set()

for it in all_idf_items:
    b, pt = extract_brand_and_type(it['title'])
    key = f"{b}_{pt}"
    if key not in seen:
        seen.add(key)
        it['brand_type'] = key
        diverse_idf.append(it)

print(f"Total Idefix pooled: {len(all_idf_items)} -> Unique diverse brand-types: {len(diverse_idf)}")
print(Counter(x.get('category') for x in diverse_idf))
