import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

nonTechKeywords = [
    'krem', 'serum', 'losyon', 'nemlendirici', 'hydro boost', 'nivea',
    'neutrogena', 'loreal', 'parfüm', 'parfum', 'deodorant', 'şampuan', 'sampuan',
    'maske', 'makyaj', 'ruj', 'rimel', 'maskara', 'cilt', 'bakım yağı', 'tonik',
    'güneş kremi', 'skinmaster', 'yüz temizleme', 'dudak', 'kolonya',
    'yelek', 'mont', 'şort', 'sort', 'kapri', 'pantolon', 't-shirt',
    'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı',
    'bot', 'çorap', 'ceket', 'gömlek', 'polar', 'tayt', 'içlik',
    'boxer', 'kaban', 'atlet', 'elbise', 'etek', 'buzluk', 'cooler'
]

for i, x in enumerate(d):
    if x['category'] == 'Teknoloji':
        t = x['title'].lower()
        matched = [k for k in nonTechKeywords if k in t]
        if matched:
            print(f"Index {i}: matched {matched} in {x['title']}")
