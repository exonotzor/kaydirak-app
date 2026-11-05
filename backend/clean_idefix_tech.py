import json

non_tech_words = [
    'mont', 'kaban', 'ceket', 'polar', 'yelek', 'şort', 'sort', 'pantolon',
    'sweatshirt', 'kazak', 'hırka', 'ayakkabı', 'bot', 'çorap', 'gömlek', 'tayt',
    'krem', 'serum', 'losyon', 'parfüm', 'parfum', 'şampuan', 'maskara', 'ruj',
    'tava', 'tencere', 'termos', 'yastık', 'nevresim', 'havlu', 'çanta', 'canta'
]

with open('backend/pool/pool_idefix.json', 'r', encoding='utf-8') as f:
    pool = json.load(f)

# Filter Teknoloji
tech_clean = []
for it in pool['Teknoloji']:
    t = it['title'].lower()
    if any(w in t for w in non_tech_words):
        continue
    # Must have tech keywords
    if any(k in t for k in ['saat', 'kronometre', 'şarj', 'sarj', 'kablo', 'kulaklık', 'kulaklik', 'hoparlör', 'hoparlor', 'pil', 'klavye', 'mouse', 'ssd', 'adaptör', 'powerbank', 'usb', 'hafıza', 'monitör', 'tablet', 'akıllı', 'bluetooth', 'mikrofon', 'webcam', 'kamera']):
        tech_clean.append(it)

print(f"Idefix Teknoloji: was {len(pool['Teknoloji'])}, now clean {len(tech_clean)}")
pool['Teknoloji'] = tech_clean

with open('backend/pool/pool_idefix.json', 'w', encoding='utf-8') as f:
    json.dump(pool, f, ensure_ascii=False, indent=2)

print("Saved clean backend/pool/pool_idefix.json")
