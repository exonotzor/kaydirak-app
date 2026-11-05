import json
import requests
import urllib3
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

with open('scraper/idefix_all_categories.json', 'r', encoding='utf-8') as f:
    all_cats = json.load(f)

print(f"Total Idefix categories available: {len(all_cats)}")

def categorize(cat_name, cat_url):
    u = cat_url.lower()
    n = cat_name.lower()
    
    # Teknoloji
    if any(k in u for k in ['elektronik', 'teknoloji', 'telefon', 'gaming', 'kulaklik', 'bilgisayar', 'tablet', 'oyuncu', 'mouse', 'klavye', 'sarj', 'kablo', 'giyilebilir', 'tv', 'ses', 'kamera']) or \
       any(k in n for k in ['telefon', 'kulaklık', 'mouse', 'klavye', 'şarj', 'kablo', 'bluetooth', 'hoparlör', 'gaming', 'elektronik']):
        return 'Teknoloji'
        
    # Kozmetik
    if any(k in u for k in ['kozmetik', 'parfum', 'cilt', 'makyaj', 'sac', 'kisisel', 'saglik', 'deodorant']) or \
       any(k in n for k in ['kozmetik', 'parfüm', 'cilt', 'makyaj', 'saç', 'kişisel', 'bakım', 'krem']):
        return 'Kozmetik'
        
    # Ev & Yaşam
    if any(k in u for k in ['ev-', 'mutfak', 'sofra', 'tekstil', 'banyo', 'aydinlatma', 'mobilya', 'dekorasyon', 'yasam', 'temizlik', 'gerecleri', 'aletleri', 'yapi-market', 'evcil']) or \
       any(k in n for k in ['ev ', 'mutfak', 'sofra', 'tekstil', 'banyo', 'aydınlatma', 'mobilya', 'dekorasyon', 'temizlik']):
        return 'Ev & Yaşam'
        
    # Moda
    if any(k in u for k in ['ayakkabi', 'canta', 'valiz', 'giyim', 'saat', 'gozluk', 'taki', 'aksesuar', 'terlik', 'bot', 'sneaker', 'mont', 'ceket', 'kadin', 'erkek', 'cocuk']) or \
       any(k in n for k in ['ayakkabı', 'çanta', 'valiz', 'giyim', 'saat', 'gözlük', 'takı', 'elbise', 'gömlek', 'pantolon', 'mont']):
        return 'Moda'
        
    return None

categorized = {'Teknoloji': [], 'Moda': [], 'Ev & Yaşam': [], 'Kozmetik': []}
for c in all_cats:
    cat = categorize(c['name'], c['url'])
    if cat:
        categorized[cat].append(c)

for k, v in categorized.items():
    print(f"  {k:15}: {len(v)} sub-categories in menu")
