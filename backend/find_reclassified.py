import json

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

non_tech = [
    'krem', 'serum', 'losyon', 'nemlendirici', 'hydro boost', 'nivea',
    'neutrogena', 'loreal', 'parfüm', 'parfum', 'deodorant', 'şampuan', 'sampuan',
    'maske', 'makyaj', 'ruj', 'rimel', 'maskara', 'cilt', 'bakım yağı', 'tonik',
    'güneş kremi', 'skinmaster', 'yüz temizleme', 'dudak', 'kolonya',
    'yelek', 'mont', 'şort', 'sort', 'kapri', 'pantolon', 't-shirt',
    'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı',
    'bot', 'çorap', 'ceket', 'gömlek', 'polar', 'tayt', 'içlik',
    'boxer', 'kaban', 'atlet', 'elbise', 'etek', 'buzluk', 'cooler'
]

def sanitize(cat, title):
    lower = title.lower()
    if cat == 'Teknoloji':
        for kw in non_tech:
            if kw in lower:
                if any(k in lower for k in ['krem', 'serum', 'losyon', 'nemlendirici', 'hydro boost', 'nivea', 'neutrogena', 'parfüm', 'parfum', 'şampuan', 'cilt']):
                    return 'Kozmetik'
                if any(k in lower for k in ['yelek', 'mont', 'şort', 'sort', 'kapri', 'pantolon', 'tişört', 'kazak', 'ayakkabı', 'bot', 'çorap', 'ceket']):
                    return 'Moda'
                return 'Ev & Yaşam'
    return cat

for i, d in enumerate(deals):
    orig_cat = d['category']
    san = sanitize(orig_cat, d['title'])
    if orig_cat != san:
        print(f"Index {i}: was {orig_cat} -> turned into {san} | {d['title']}")
