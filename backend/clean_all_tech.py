import json

non_tech_words = [
    'mont', 'kaban', 'ceket', 'polar', 'yelek', 'şort', 'sort', 'pantolon',
    'sweatshirt', 'kazak', 'hırka', 'ayakkabı', 'bot', 'çorap', 'gömlek', 'tayt',
    'krem', 'serum', 'losyon', 'parfüm', 'parfum', 'şampuan', 'maskara', 'ruj',
    'tava', 'tencere', 'termos', 'yastık', 'nevresim', 'havlu', 'çanta', 'canta'
]

for filename in ['pool_amazon.json', 'pool_hepsiburada.json']:
    path = f'backend/pool/{filename}'
    with open(path, 'r', encoding='utf-8') as f:
        pool = json.load(f)
    
    cleaned = []
    for it in pool['Teknoloji']:
        t = it['title'].lower()
        if not any(w in t for w in non_tech_words):
            cleaned.append(it)
            
    print(f"{filename} Teknoloji: was {len(pool['Teknoloji'])}, now {len(cleaned)}")
    pool['Teknoloji'] = cleaned
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)
