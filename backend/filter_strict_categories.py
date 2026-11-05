import json
import glob

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

for p in glob.glob('backend/pool/*.json'):
    with open(p, 'r', encoding='utf-8') as f:
        pool = json.load(f)
    
    cleaned = {}
    for cat, items in pool.items():
        kept = []
        for it in items:
            t = it.get('title', '')
            if sanitize(cat, t) == cat:
                kept.append(it)
            else:
                print(f"Removed from {p} [{cat}]: {t[:50]}")
        cleaned[cat] = kept
        
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

print("All pools strictly aligned with Dart sanitizeCategory!")
