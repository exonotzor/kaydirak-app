import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    tech = json.load(f)

# Find genuine tech
non_tech_words = [
    'parka', 'kaban', 'ceket', 'mont', 'yelek', 'şort', 'sort', 'kapri', 'pantolon',
    't-shirt', 'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı', 'bot',
    'çorap', 'gömlek', 'polar', 'tayt', 'içlik', 'boxer', 'atlet', 'elbise', 'etek',
    'buzluk', 'cooler', 'stein', 'bardak', 'termos', 'matara', 'tava', 'tencere', 'krampon',
    'çanta', 'canta', 'tozluk', 'eldiven', 'bere', 'şapka', 'sapka', 'bikini', 'mayo',
    'krem', 'serum', 'losyon', 'deodorant', 'parfüm'
]

pure_idefix_tech = []
for x in tech:
    t = x.get('title', '').lower()
    if not any(w in t for w in non_tech_words):
        if any(k in t for k in ['saat', 'kronometre', 'şarj', 'sarj', 'kablo', 'kulaklık', 'kulaklik', 'hoparlör', 'hoparlor', 'pil', 'klavye', 'mouse', 'webcam', 'etiket makinesi', 'koşu bandı']):
            pure_idefix_tech.append(x)

print(f"Total pure Idefix electronic gadgets found: {len(pure_idefix_tech)}")
for i, x in enumerate(pure_idefix_tech[:15]):
    print(f"{i+1:2d}. %{x.get('discountRate')} | {x.get('title')[:65]}")
