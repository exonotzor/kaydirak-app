import json
from collections import Counter

with open('scraper/amazon_verified_deals.json', 'r', encoding='utf-8') as f:
    amz = json.load(f)

def extract_brand_and_type(title):
    t = title.lower()
    brand = 'diger'
    for b in ['samsung', 'apple', 'baseus', 'anker', 'logitech', 'philips', 't-dagger', 'lexibook', 'calvin klein', 'tommy jeans', 'only & sons', 'defacto', 'madmext', 'emsan', 'karaca', 'bonera', 'nivea', 'neutrogena', 'loreal', "l'oreal", 'garnier', 'colgate', 'tefal', 'stanley', 'puma', 'adidas']:
        if b in t:
            brand = b.replace(' ', '').replace('&', '').replace("'", '')
            break
    if brand == 'diger':
        brand = t.split()[0] if t.split() else 'unknown'

    ptype = 'diger'
    for pt in ['kulaklik', 'kulaklık', 'mouse', 'klavye', 'powerbank', 'saat', 'hoparlor', 'hoparlör', 'pil', 'kablo', 'mont', 'ceket', 'sweatshirt', 'gomlek', 'gömlek', 'kazak', 'pantolon', 'tshirt', 'tişört', 'ayakkabi', 'ayakkabı', 'tencere', 'tava', 'termos', 'krem', 'serum', 'parfum', 'parfüm', 'losyon']:
        if pt in t:
            ptype = pt.replace('ı', 'i').replace('ş', 's').replace('ç', 'c').replace('ö', 'o').replace('ü', 'u').replace('ğ', 'g')
            break
    return brand, ptype

diverse_amz = []
seen = set()
for d in amz:
    b, pt = extract_brand_and_type(d['title'])
    key = f"{b}_{pt}"
    if key not in seen:
        seen.add(key)
        d['brand_type'] = key
        diverse_amz.append(d)

print(f"Total Amazon: {len(amz)} -> Unique diverse brand-types: {len(diverse_amz)}")
print("Categories:", Counter(x['category'] for x in diverse_amz))
for cat in ['Teknoloji', 'Moda', 'Ev & Yaşam', 'Kozmetik']:
    sub = [x for x in diverse_amz if x['category'] == cat]
    print(f"\n--- {cat} ({len(sub)}) ---")
    for s in sub[:5]:
        print(f"  {s['brand_type']}: {s['title'][:40]} (%{s['discountRate']})")
