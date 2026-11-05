import json
from collections import Counter

# --- AMAZON TR (20 items: 5 Teknoloji, 5 Moda, 5 Ev & Yaşam, 5 Kozmetik) ---
with open('scraper/amazon_verified_deals.json', 'r', encoding='utf-8') as f:
    amz_raw = json.load(f)

# --- HEPSIBURADA (20 items: 6 Teknoloji, 7 Moda, 7 Ev & Yaşam) ---
with open('scraper/hepsiburada_verified_deals.json', 'r', encoding='utf-8') as f:
    hb_raw = json.load(f)

# --- IDEFIX (20 items: 5 Teknoloji, 5 Moda, 5 Ev & Yaşam, 5 Kozmetik) ---
with open('scraper/idefix_strict_onpage.json', 'r', encoding='utf-8') as f:
    idf_raw = json.load(f)
with open('scraper/home_beauty_strict.json', 'r', encoding='utf-8') as f:
    idf_hb = json.load(f)
with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    idf_tech = json.load(f)

print("Amazon pool:", len(amz_raw))
print("HB pool:", len(hb_raw))
print("Idefix pool:", len(idf_raw), len(idf_hb), len(idf_tech))

# Amazon selection
amz_curated = []
# Teknoloji
for t in [x for x in amz_raw if x['category'] == 'Teknoloji']:
    if 'powerbank' in t['title'].lower() or 'mouse' in t['title'].lower() or 'kulak' in t['title'].lower() or 'pil' in t['title'].lower():
        if not any(x['title'][:15] == t['title'][:15] for x in amz_curated):
            amz_curated.append(t)
            if len([x for x in amz_curated if x['category'] == 'Teknoloji']) >= 5:
                break
# Moda
for m in [x for x in amz_raw if x['category'] == 'Moda']:
    if not any(x['title'][:15] == m['title'][:15] for x in amz_curated):
        amz_curated.append(m)
        if len([x for x in amz_curated if x['category'] == 'Moda']) >= 5:
            break
# Ev & Yaşam
for e in [x for x in amz_raw if x['category'] == 'Ev & Yaşam']:
    if not any(x['title'][:15] == e['title'][:15] for x in amz_curated):
        amz_curated.append(e)
        if len([x for x in amz_curated if x['category'] == 'Ev & Yaşam']) >= 5:
            break
# Kozmetik
for k in [x for x in amz_raw if x['category'] == 'Kozmetik']:
    if not any(x['title'][:15] == k['title'][:15] for x in amz_curated):
        amz_curated.append(k)
        if len([x for x in amz_curated if x['category'] == 'Kozmetik']) >= 5:
            break

print("Amz curated:", len(amz_curated), Counter(x['category'] for x in amz_curated))

# HB selection (20 items)
hb_curated = []
# Remove near duplicates (e.g. only 1 color of Redmi Buds 6, 2 colors of US Polo)
seen_hb_brands = Counter()
for it in hb_raw:
    # identify brand or core title
    brand_key = it['title'].split()[0].lower()
    if 'redmi' in it['title'].lower() or 'xiaomi' in it['title'].lower():
        brand_key = 'xiaomi'
    elif 'polo' in it['title'].lower():
        brand_key = 'uspolo'
    elif 'stanley' in it['title'].lower():
        brand_key = 'stanley'
    elif 'havit' in it['title'].lower():
        brand_key = 'havit'
        
    if seen_hb_brands[brand_key] < 2:  # at most 2 per brand for variety
        seen_hb_brands[brand_key] += 1
        hb_curated.append(it)
    elif len(hb_curated) < 20 and seen_hb_brands[brand_key] < 3:
        seen_hb_brands[brand_key] += 1
        hb_curated.append(it)

# fill up to 20 if needed
for it in hb_raw:
    if len(hb_curated) >= 20:
        break
    if it not in hb_curated:
        hb_curated.append(it)

print("HB curated:", len(hb_curated), Counter(x['category'] for x in hb_curated))

# Idefix selection (20 items)
idf_curated = []
# Teknoloji (Casio, Spovan, etc. NO duplicate stopwatches)
tech_cands = [
    x for x in idf_tech 
    if any(k in x['title'].lower() for k in ['casio erkek', 'spovan ring', 'spovan vision', 'spovan cardio', 'spovan electro'])
    and 'kronometre' not in x['title'].lower()
]
for t in tech_cands[:5]:
    t['category'] = 'Teknoloji'
    idf_curated.append(t)

# Moda (Benetton, Muggo, ONL, etc.)
for m in [x for x in idf_raw if x.get('category') == 'Moda']:
    if not any(x['title'][:15] == m['title'][:15] for x in idf_curated):
        idf_curated.append(m)
        if len([x for x in idf_curated if x.get('category') == 'Moda']) >= 5:
            break

# Ev & Yaşam (Nehir cookware, kitchen)
for e in [x for x in idf_hb + idf_raw if x.get('category') == 'Ev & Yaşam']:
    if not any(x['title'][:15] == e['title'][:15] for x in idf_curated):
        idf_curated.append(e)
        if len([x for x in idf_curated if x.get('category') == 'Ev & Yaşam']) >= 5:
            break

# Kozmetik (Siveno, Erbatab)
for k in [x for x in idf_hb if x.get('category') == 'Kozmetik']:
    if not any(x['title'][:15] == k['title'][:15] for x in idf_curated):
        idf_curated.append(k)
        if len([x for x in idf_curated if x.get('category') == 'Kozmetik']) >= 5:
            break

print("Idefix curated:", len(idf_curated), Counter(x['category'] for x in idf_curated))
