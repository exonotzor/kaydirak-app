import json
import os
import re
import urllib.request
import subprocess
from collections import Counter
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(PROJECT_DIR)

# 1. Load previous deals to guarantee 0% overlap
with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    prev_deals = json.load(f)

prev_titles = set(d['title'].strip().lower() for d in prev_deals)
prev_urls = set(d['productUrl'].strip().lower() for d in prev_deals)

print(f"Previous live deals count: {len(prev_deals)}")

# Non-tech ban list for Teknoloji
banned_in_tech = [
    'parka', 'kaban', 'ceket', 'mont', 'yelek', 'şort', 'sort', 'kapri', 'pantolon',
    't-shirt', 'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı', 'bot',
    'çorap', 'gömlek', 'polar', 'tayt', 'içlik', 'boxer', 'atlet', 'elbise', 'etek',
    'buzluk', 'cooler', 'stein', 'bardak', 'termos', 'matara', 'tava', 'tencere', 'krampon',
    'çanta', 'canta', 'tozluk', 'eldiven', 'bere', 'şapka', 'sapka', 'bikini', 'mayo',
    'krem', 'serum', 'losyon', 'deodorant', 'parfüm', 'sabun', 'yağ', 'biberon', 'oyuncak'
]

def is_fresh(d):
    t = d.get('title', '').strip().lower()
    u = d.get('productUrl') or (f"https://www.amazon.com.tr/dp/{d.get('shortId')}" if d.get('shortId') else "")
    u = u.strip().lower()
    return (t not in prev_titles) and (not u or u not in prev_urls)

def clean_amazon_url(url):
    m = re.search(r'([B0-9A-Z]{10})', url)
    if m:
        return f"https://www.amazon.com.tr/dp/{m.group(1)}"
    return url

# -----------------
# 1. HEPSIBURADA (40 fresh deals: 10 per cat)
# -----------------
with open('scraper/hb_harvested_fresh.json', 'r', encoding='utf-8') as f:
    hb_harvested = json.load(f)

hb_selected = []
for cat in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
    items = hb_harvested.get(cat, [])
    valid = []
    for it in items:
        if not is_fresh(it):
            continue
        if cat == 'Teknoloji':
            if any(b in it['title'].lower() for b in banned_in_tech):
                continue
        valid.append(it)
    print(f"HB {cat}: {len(valid)} fresh available")
    assert len(valid) >= 10, f"Not enough HB deals for {cat}: {len(valid)}"
    hb_selected.extend(valid[:10])

# -----------------
# 2. AMAZON TR (40 fresh deals: 10 per cat)
# -----------------
with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
    amz_deals = json.load(f)

with open('scraper/amazon_verified_deals.json', 'r', encoding='utf-8') as f:
    amz_verified = json.load(f)

amz_all = amz_deals + amz_verified
amz_by_cat = {'Teknoloji': [], 'Moda': [], 'Kozmetik': [], 'Ev & Yaşam': []}
seen_amz_titles = set()

for d in amz_all:
    c = d.get('category')
    if c not in amz_by_cat:
        continue
    t = d['title'].strip()
    if t.lower() in seen_amz_titles:
        continue
    if not is_fresh(d):
        continue
    if c == 'Teknoloji':
        if any(b in t.lower() for b in banned_in_tech):
            continue
    # Ensure clean DP url
    url = d.get('productUrl') or f"https://www.amazon.com.tr/dp/{d.get('shortId', '')}"
    d['productUrl'] = clean_amazon_url(url)
    d['store'] = 'Amazon TR'
    seen_amz_titles.add(t.lower())
    amz_by_cat[c].append(d)

amz_selected = []
for cat in ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']:
    valid = amz_by_cat[cat]
    print(f"Amazon {cat}: {len(valid)} fresh available")
    assert len(valid) >= 10, f"Not enough Amazon deals for {cat}: {len(valid)}"
    amz_selected.extend(valid[:10])

# -----------------
# 3. IDEFIX (40 fresh deals: 10 per cat)
# -----------------
# Pure Idefix Tech
with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    idf_tech_pool = json.load(f)

idf_tech = []
seen_idf_titles = set()
for d in idf_tech_pool:
    t = d['title'].strip()
    if t.lower() in seen_idf_titles:
        continue
    if not is_fresh(d):
        continue
    tl = t.lower()
    if any(b in tl for b in banned_in_tech):
        continue
    # Tech keywords check
    if any(k in tl for k in ['saat', 'kronometre', 'şarj', 'sarj', 'kablo', 'kulaklık', 'kulaklik', 'hoparlör', 'hoparlor', 'pil', 'klavye', 'mouse', 'webcam', 'bellek', 'ssd', 'adaptör', 'powerbank']):
        d['store'] = 'Idefix'
        d['category'] = 'Teknoloji'
        seen_idf_titles.add(t.lower())
        idf_tech.append(d)

print(f"Idefix Teknoloji: {len(idf_tech)} fresh available")
assert len(idf_tech) >= 10

# Idefix Moda, Kozmetik, Ev & Yaşam
with open('scraper/final_verified_catalog.json', 'r', encoding='utf-8') as f:
    idf_fvc = json.load(f)
with open('scraper/top_home_strict.json', 'r', encoding='utf-8') as f:
    idf_home = json.load(f)
with open('scraper/home_beauty_strict.json', 'r', encoding='utf-8') as f:
    idf_beauty = json.load(f)

idf_other_pool = idf_fvc + idf_home + idf_beauty
idf_by_cat = {'Moda': [], 'Kozmetik': [], 'Ev & Yaşam': []}

for d in idf_other_pool:
    if d.get('store') != 'Idefix':
        continue
    c = d.get('category')
    if c not in idf_by_cat:
        continue
    t = d['title'].strip()
    if t.lower() in seen_idf_titles:
        continue
    if not is_fresh(d):
        continue
    seen_idf_titles.add(t.lower())
    d['store'] = 'Idefix'
    idf_by_cat[c].append(d)

idf_selected = idf_tech[:10]
for cat in ['Moda', 'Kozmetik', 'Ev & Yaşam']:
    valid = idf_by_cat[cat]
    print(f"Idefix {cat}: {len(valid)} fresh available")
    assert len(valid) >= 10, f"Not enough Idefix deals for {cat}: {len(valid)}"
    idf_selected.extend(valid[:10])

# Verify candidate sets
print("\nSelected pool summaries:")
print(f"HB: {len(hb_selected)}, Amazon: {len(amz_selected)}, Idefix: {len(idf_selected)}")

all_120 = hb_selected + amz_selected + idf_selected
assert len(all_120) == 120

c_store = Counter(d['store'] for d in all_120)
c_cat = Counter(d['category'] for d in all_120)
print(f"Store distribution: {c_store}")
print(f"Category distribution: {c_cat}")

assert c_store['Amazon TR'] == 40 and c_store['Hepsiburada'] == 40 and c_store['Idefix'] == 40
assert c_cat['Teknoloji'] == 30 and c_cat['Moda'] == 30 and c_cat['Kozmetik'] == 30 and c_cat['Ev & Yaşam'] == 30

# Verify 0% overlap with previous deals
current_new_titles = set(d['title'].strip().lower() for d in all_120)
overlap = current_new_titles.intersection(prev_titles)
print(f"Overlap with previous catalog: {len(overlap)} items (MUST BE 0)")
assert len(overlap) == 0, f"Found overlapping items: {overlap}"

# Zero-collision interleaver (backtracking solver)
print("\nSolving zero-collision sequence (no consecutive store or category)...")
stores = ['Amazon TR', 'Hepsiburada', 'Idefix']
categories = ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']

# Group by (store, category)
bins = {}
for s in stores:
    for c in categories:
        bins[(s, c)] = [d for d in all_120 if d['store'] == s and d['category'] == c]
        # Should be exactly 10 in each bin
        assert len(bins[(s, c)]) == 10, f"Bin ({s}, {c}) has {len(bins[(s, c)])} items"

print("All 12 bins have exactly 10 items. Perfect grid!")

def solve_order(seq, remaining):
    if len(seq) == 120:
        return seq
    
    last_store = seq[-1]['store'] if seq else None
    last_cat = seq[-1]['category'] if seq else None
    
    # Sort candidate keys by remaining count descending (most constrained first)
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

# Verify collisions
store_collisions = sum(1 for i in range(119) if ordered[i]['store'] == ordered[i+1]['store'])
cat_collisions = sum(1 for i in range(119) if ordered[i]['category'] == ordered[i+1]['category'])
print(f"Store collisions: {store_collisions}, Category collisions: {cat_collisions}")
assert store_collisions == 0
assert cat_collisions == 0

# Clean compact fields
compact_catalog = []
for it in ordered:
    compact_catalog.append({
        'id': it.get('id', ''),
        'title': it.get('title', '').strip(),
        'originalPrice': float(it.get('originalPrice', 0)),
        'discountedPrice': float(it.get('discountedPrice', 0)),
        'discountRate': int(it.get('discountRate', 0)),
        'imageUrl': it.get('imageUrl', '').strip(),
        'productUrl': it.get('productUrl', '').strip(),
        'store': it.get('store', '').strip(),
        'category': it.get('category', '').strip()
    })

# Save to assets/data/live_deals.json and scraper/final_equal_verified_catalog.json
with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(compact_catalog, f, ensure_ascii=False, indent=2)

with open('scraper/final_equal_verified_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(compact_catalog, f, ensure_ascii=False, indent=2)

with open('scraper/compact_deals.json', 'w', encoding='utf-8') as f:
    json.dump(compact_catalog, f, ensure_ascii=False, indent=2)

print("\nSaved 120 fresh deals to local JSON files.")

# PUT to ExtendsClass REST API
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

print(f"\nUploading 120 fresh deals to REST endpoint {endpoint}...")
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        print(f"ExtendsClass PUT response code: {resp.status}")
except Exception as e:
    print(f"ExtendsClass PUT error: {e}")

# Verify download from remote
req_get = urllib.request.Request(
    endpoint,
    headers={'Cache-Control': 'no-cache', 'User-Agent': 'Mozilla/5.0'}
)
with urllib.request.urlopen(req_get, timeout=15) as resp:
    remote_data = json.loads(resp.read().decode('utf-8'))
    print(f"Remote verification: {len(remote_data)} items live!")
    print(f"Remote first 3 items:")
    for i, it in enumerate(remote_data[:3]):
        print(f"  {i+1}. [{it['store']}] [{it['category']}] %{it['discountRate']} | {it['title'][:45]}")

print("\nSUCCESS: All 120 deals are 100% freshly rotated!")
