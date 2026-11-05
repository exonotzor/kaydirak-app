import json
import glob
from collections import Counter
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Load current 120 catalog
with open('assets/data/live_deals.json', 'r', encoding='utf-8') as fp:
    current = json.load(fp)

current_titles = set(x['title'][:25].lower() for x in current)
print(f"Current catalog size: {len(current)}")

# Collect all pool items
all_pools = []
for f in glob.glob('scraper/*.json'):
    if any(k in f for k in ['final', 'compact', 'live_deals', 'sample']):
        continue
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            d = json.load(fp)
            if isinstance(d, list):
                all_pools.extend(d)
    except:
        pass

print(f"Total raw items gathered: {len(all_pools)}")

# Filter and clean fresh items
banned_in_tech = [
    'parka', 'kaban', 'ceket', 'mont', 'yelek', 'şort', 'sort', 'kapri', 'pantolon',
    't-shirt', 'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı', 'bot',
    'çorap', 'gömlek', 'polar', 'tayt', 'içlik', 'boxer', 'atlet', 'elbise', 'etek',
    'buzluk', 'cooler', 'stein', 'bardak', 'termos', 'matara', 'tava', 'tencere', 'krampon',
    'çanta', 'canta', 'tozluk', 'eldiven', 'bere', 'şapka', 'sapka', 'bikini', 'mayo',
    'krem', 'serum', 'losyon', 'deodorant', 'parfüm', 'sabun'
]

def classify(it):
    title = it.get('title', '').strip()
    t_low = title.lower()
    cat = it.get('category', '').strip()

    if any(k in t_low for k in ['krem', 'serum', 'losyon', 'nemlendirici', 'hydro boost', 'nivea', 'neutrogena', 'loreal', 'parfüm', 'parfum', 'deodorant', 'şampuan', 'sampuan', 'maske', 'makyaj', 'ruj', 'rimel', 'maskara', 'cilt', 'bakım yağı', 'tonik', 'güneş kremi', 'skinmaster', 'yüz temizleme', 'dudak', 'kolonya', 'parfüm']):
        return 'Kozmetik'
    if any(k in t_low for k in ['yelek', 'mont', 'şort', 'sort', 'kapri', 'pantolon', 't-shirt', 'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı', 'bot', 'çorap', 'ceket', 'gömlek', 'polar', 'tayt', 'içlik', 'boxer', 'kaban', 'atlet', 'elbise', 'etek', 'benetton', 'puma', 'nike', 'skechers']):
        return 'Moda'
    if any(k in t_low for k in ['buzluk', 'termos', 'fincan', 'tava', 'tencere', 'tabak', 'nevresim', 'yastık', 'yorgan', 'havlu', 'deterjan', 'yumuşatıcı', 'sabun', 'cooler']):
        return 'Ev & Yaşam'
    if cat == 'Teknoloji' or any(k in t_low for k in ['kulaklık', 'hoparlör', 'powerbank', 'şarj', 'kablo', 'mouse', 'klavye', 'webcam', 'saat', 'kronometre', 'pil', 'tıraş makinesi', 'wifi', 'modem', 'ssd', 'usb', 'hafıza kartı', 'koşu bandı']):
        if not any(w in t_low for w in banned_in_tech):
            return 'Teknoloji'
    return cat if cat in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam'] else 'Ev & Yaşam'

unique_fresh = {}
for it in all_pools:
    title = it.get('title', '').strip()
    if len(title) < 10:
        continue
    k = title[:25].lower()
    if k in current_titles or k in unique_fresh:
        continue
    
    orig = float(it.get('originalPrice', 0))
    disc = float(it.get('discountedPrice', 0))
    rate = int(it.get('discountRate', 0))
    if orig <= disc or disc <= 0 or rate < 15:
        continue
    
    purl = it.get('productUrl', '')
    iurl = it.get('imageUrl', '')
    if not purl.startswith('http') or not iurl.startswith('http'):
        continue

    store = it.get('store', '')
    if store not in ['Amazon TR', 'Hepsiburada', 'Idefix']:
        continue

    cat = classify(it)
    # Strict reject non-tech in tech
    if cat == 'Teknoloji' and any(w in it['title'].lower() for w in banned_in_tech):
        continue

    unique_fresh[k] = {
        'title': title,
        'category': cat,
        'store': store,
        'originalPrice': orig,
        'discountedPrice': disc,
        'discountRate': rate,
        'productUrl': purl,
        'imageUrl': iurl
    }

print(f"Total clean, unique FRESH candidates: {len(unique_fresh)}")
fresh_list = list(unique_fresh.values())
print("Stores distribution:", dict(Counter(x['store'] for x in fresh_list)))
print("Category distribution:", dict(Counter(x['category'] for x in fresh_list)))

# Group by (category, store)
matrix = {}
for c in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
    for s in ['Amazon TR', 'Hepsiburada', 'Idefix']:
        cnt = len([x for x in fresh_list if x['category'] == c and x['store'] == s])
        matrix[(c, s)] = cnt

print("\nFresh Items Matrix (Need 10 for each):")
for c in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
    row = [f"{s}: {matrix[(c, s)]}" for s in ['Amazon TR', 'Hepsiburada', 'Idefix']]
    print(f"  {c:11s} -> {', '.join(row)}")
