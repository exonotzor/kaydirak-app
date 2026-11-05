import json
import os
import re
import csv
import urllib.request
from collections import Counter
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(PROJECT_DIR)

# 1. Collect all previously seen titles from CSV and previous catalogs
banned_titles = set()
with open('YariFiyatina_Urun_Listesi_Dogrulanmis.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for r in list(reader)[1:]:
        if len(r) > 4:
            banned_titles.add(r[4].strip().lower())

print(f"Loaded {len(banned_titles)} banned titles from original CSV.")

banned_in_tech = [
    'parka', 'kaban', 'ceket', 'mont', 'yelek', 'şort', 'sort', 'kapri', 'pantolon',
    't-shirt', 'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı', 'bot',
    'çorap', 'gömlek', 'polar', 'tayt', 'içlik', 'boxer', 'atlet', 'elbise', 'etek',
    'buzluk', 'cooler', 'stein', 'bardak', 'termos', 'matara', 'tava', 'tencere', 'krampon',
    'çanta', 'canta', 'tozluk', 'eldiven', 'bere', 'şapka', 'sapka', 'bikini', 'mayo',
    'krem', 'serum', 'losyon', 'deodorant', 'parfüm', 'sabun', 'yağ', 'biberon', 'oyuncak'
]

def clean_amazon_url(url):
    m = re.search(r'([B0-9A-Z]{10})', url)
    if m:
        return f"https://www.amazon.com.tr/dp/{m.group(1)}"
    return url

def is_valid_deal(d, cat):
    t = d.get('title', '').strip()
    if not t or len(t) < 5:
        return False
    if t.lower() in banned_titles:
        return False
        
    orig = float(d.get('originalPrice', 0))
    disc = float(d.get('discountedPrice', 0))
    rate = int(d.get('discountRate', 0))
    
    # Realistic discount criteria
    if not (15 <= rate <= 75):
        return False
    if disc < 50:
        return False
    if orig > 4.0 * disc:
        return False
        
    if cat == 'Teknoloji':
        tl = t.lower()
        if any(b in tl for b in banned_in_tech):
            return False
            
    return True

# -----------------
# 1. HEPSIBURADA
# -----------------
with open('scraper/hb_harvested_fresh.json', 'r', encoding='utf-8') as f:
    hb_harvested = json.load(f)

hb_selected = []
for cat in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
    items = hb_harvested.get(cat, [])
    valid = []
    seen = set()
    for it in items:
        t = it['title'].strip().lower()
        if t in seen:
            continue
        if is_valid_deal(it, cat):
            seen.add(t)
            valid.append(it)
    print(f"HB {cat}: {len(valid)} fresh valid deals")
    assert len(valid) >= 10, f"Insufficient HB deals for {cat}: {len(valid)}"
    hb_selected.extend(valid[:10])

# -----------------
# 2. AMAZON TR
# -----------------
with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
    amz_deals = json.load(f)
with open('scraper/amazon_verified_deals.json', 'r', encoding='utf-8') as f:
    amz_verified = json.load(f)

amz_by_cat = {'Teknoloji': [], 'Moda': [], 'Kozmetik': [], 'Ev & Yaşam': []}
seen_amz = set()

for d in amz_deals + amz_verified:
    c = d.get('category')
    if c not in amz_by_cat:
        continue
    t = d.get('title', '').strip()
    if t.lower() in seen_amz:
        continue
    if not is_valid_deal(d, c):
        continue
    url = d.get('productUrl') or f"https://www.amazon.com.tr/dp/{d.get('shortId', '')}"
    d['productUrl'] = clean_amazon_url(url)
    d['store'] = 'Amazon TR'
    seen_amz.add(t.lower())
    amz_by_cat[c].append(d)

amz_selected = []
for cat in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
    valid = amz_by_cat[cat]
    print(f"Amazon {cat}: {len(valid)} fresh valid deals")
    assert len(valid) >= 10, f"Insufficient Amazon deals for {cat}: {len(valid)}"
    amz_selected.extend(valid[:10])

# -----------------
# 3. IDEFIX
# -----------------
with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    idf_tech_pool = json.load(f)

idf_tech = []
seen_idf = set()
for d in idf_tech_pool:
    t = d.get('title', '').strip()
    if t.lower() in seen_idf:
        continue
    if not is_valid_deal(d, 'Teknoloji'):
        continue
    tl = t.lower()
    if any(k in tl for k in ['saat', 'kronometre', 'şarj', 'sarj', 'kablo', 'kulaklık', 'kulaklik', 'hoparlör', 'hoparlor', 'pil', 'klavye', 'mouse', 'webcam', 'bellek', 'ssd', 'adaptör', 'powerbank']):
        d['store'] = 'Idefix'
        d['category'] = 'Teknoloji'
        seen_idf.add(t.lower())
        idf_tech.append(d)

print(f"Idefix Teknoloji: {len(idf_tech)} fresh valid deals")
assert len(idf_tech) >= 10

with open('scraper/final_verified_catalog.json', 'r', encoding='utf-8') as f:
    idf_fvc = json.load(f)
with open('scraper/top_home_strict.json', 'r', encoding='utf-8') as f:
    idf_home = json.load(f)
with open('scraper/home_beauty_strict.json', 'r', encoding='utf-8') as f:
    idf_beauty = json.load(f)

idf_by_cat = {'Moda': [], 'Kozmetik': [], 'Ev & Yaşam': []}
for d in idf_fvc + idf_home + idf_beauty:
    if d.get('store') != 'Idefix':
        continue
    c = d.get('category')
    if c not in idf_by_cat:
        continue
    t = d.get('title', '').strip()
    if t.lower() in seen_idf:
        continue
    if not is_valid_deal(d, c):
        continue
    seen_idf.add(t.lower())
    d['store'] = 'Idefix'
    idf_by_cat[c].append(d)

idf_selected = idf_tech[:10]
for cat in ['Moda', 'Kozmetik', 'Ev & Yaşam']:
    valid = idf_by_cat[cat]
    print(f"Idefix {cat}: {len(valid)} fresh valid deals")
    assert len(valid) >= 10, f"Insufficient Idefix deals for {cat}: {len(valid)}"
    idf_selected.extend(valid[:10])

# Assembly & Balance Validation
all_120 = hb_selected + amz_selected + idf_selected
assert len(all_120) == 120

c_store = Counter(d['store'] for d in all_120)
c_cat = Counter(d['category'] for d in all_120)
print(f"\nFinal store distribution: {c_store}")
print(f"Final category distribution: {c_cat}")

assert c_store['Amazon TR'] == 40 and c_store['Hepsiburada'] == 40 and c_store['Idefix'] == 40
assert c_cat['Teknoloji'] == 30 and c_cat['Moda'] == 30 and c_cat['Kozmetik'] == 30 and c_cat['Ev & Yaşam'] == 30

# Interleaving Solver (Backtracking)
stores = ['Amazon TR', 'Hepsiburada', 'Idefix']
categories = ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']

bins = {}
for s in stores:
    for c in categories:
        bins[(s, c)] = [d for d in all_120 if d['store'] == s and d['category'] == c]
        assert len(bins[(s, c)]) == 10

def solve_order(seq, remaining):
    if len(seq) == 120:
        return seq
    
    last_store = seq[-1]['store'] if seq else None
    last_cat = seq[-1]['category'] if seq else None
    
    candidates = []
    for (s, c), items in remaining.items():
        if len(items) > 0 and s != last_store and c != last_cat:
            candidates.append(((s, c), len(items)))
            
    candidates.sort(key=lambda x: -x[1])
    
    for (s, c), _ in candidates:
        item = remaining[(s, c)].pop()
        seq.append(item)
        res = solve_order(seq, remaining)
        if res is not None:
            return res
        seq.pop()
        remaining[(s, c)].append(item)
        
    return None

ordered = solve_order([], {k: list(v) for k, v in bins.items()})
assert ordered is not None and len(ordered) == 120

# Check collisions
store_collisions = sum(1 for i in range(119) if ordered[i]['store'] == ordered[i+1]['store'])
cat_collisions = sum(1 for i in range(119) if ordered[i]['category'] == ordered[i+1]['category'])
print(f"Store collisions: {store_collisions}, Category collisions: {cat_collisions}")
assert store_collisions == 0
assert cat_collisions == 0

compact_catalog = []
for it in ordered:
    compact_catalog.append({
        'id': it.get('id', ''),
        'title': it.get('title', '').strip(),
        'originalPrice': round(float(it.get('originalPrice', 0)), 2),
        'discountedPrice': round(float(it.get('discountedPrice', 0)), 2),
        'discountRate': int(it.get('discountRate', 0)),
        'imageUrl': it.get('imageUrl', '').strip(),
        'productUrl': it.get('productUrl', '').strip(),
        'store': it.get('store', '').strip(),
        'category': it.get('category', '').strip()
    })

# Save to disk
with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(compact_catalog, f, ensure_ascii=False, indent=2)

with open('scraper/final_equal_verified_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(compact_catalog, f, ensure_ascii=False, indent=2)

with open('scraper/compact_deals.json', 'w', encoding='utf-8') as f:
    json.dump(compact_catalog, f, ensure_ascii=False, indent=2)

# Upload to ExtendsClass
endpoint = "https://extendsclass.com/api/json-storage/bin/ccbacbe"
payload = json.dumps(compact_catalog, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    endpoint,
    data=payload,
    headers={
        'Content-Type': 'application/json',
        'User-Agent': 'Antigravity-Rotation-Engine/2.0'
    },
    method='PUT'
)

with urllib.request.urlopen(req, timeout=15) as resp:
    print(f"ExtendsClass PUT HTTP status: {resp.status}")

# Verify GET from remote
req_get = urllib.request.Request(
    endpoint,
    headers={'Cache-Control': 'no-cache', 'User-Agent': 'Mozilla/5.0'}
)
with urllib.request.urlopen(req_get, timeout=15) as resp:
    remote_data = json.loads(resp.read().decode('utf-8'))
    print(f"\nRemote confirmation: {len(remote_data)} deals are LIVE on {endpoint}!")
    print("Top 6 deals currently live for the user:")
    for i, it in enumerate(remote_data[:6]):
        print(f"  {i+1}. [{it['store']}] [{it['category']}] %{it['discountRate']} | {it['originalPrice']} TL -> {it['discountedPrice']} TL | {it['title'][:55]}")

print("\nCOMPLETE SUCCESS! Ready for user pull-to-refresh.")
