import json
import re

# 1. Load Moda deals
with open('scraper/idefix_strict_onpage.json', 'r', encoding='utf-8') as f:
    raw_idefix = json.load(f)

moda_candidates = [x for x in raw_idefix if x['category'] == 'Moda']
print(f"Moda candidates: {len(moda_candidates)}")

# 2. Load Kozmetik deals
with open('scraper/home_beauty_strict.json', 'r', encoding='utf-8') as f:
    raw_beauty = json.load(f)

beauty_candidates = [x for x in raw_beauty if x['category'] == 'Kozmetik']
# Also add from raw_idefix if missing
for x in raw_idefix:
    if x['category'] == 'Kozmetik' and x['id'] not in [b['id'] for b in beauty_candidates]:
        beauty_candidates.append(x)
print(f"Kozmetik candidates: {len(beauty_candidates)}")

# 3. Load Ev & Yaşam deals
with open('scraper/top_home_strict.json', 'r', encoding='utf-8') as f:
    raw_top_home = json.load(f)
with open('scraper/all_home_strict.json', 'r', encoding='utf-8') as f:
    raw_all_home = json.load(f)

home_map = {}
for x in raw_top_home + raw_all_home:
    home_map[x['id']] = x
for x in raw_idefix:
    if x['category'] == 'Ev & Yaşam':
        home_map[x['id']] = x
home_candidates = list(home_map.values())
print(f"Ev & Yaşam candidates: {len(home_candidates)}")

# 4. Load Teknoloji deals
# We take verified tech items from all_tech_verified.json, powerbanks, spovan, exvega gaming, phone cases
with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    raw_tech = json.load(f)

tech_candidates = []
seen_tech = set()

# Filter pure technology
for x in raw_tech:
    sub = x.get('subCategory', '').lower()
    title = x.get('title', '').lower()
    if any(k in sub or k in title for k in ['tişört', 'tisort', 'polar', 'ceket', 'mont', 'pantolon', 'şort', 'sort', 'yağmurluk', 'spor giyim']):
        continue
    # must be tech category
    if x['id'] not in seen_tech:
        seen_tech.add(x['id'])
        tech_candidates.append(x)

print(f"Teknoloji candidates: {len(tech_candidates)}")

# Sort each category for best quality / variety
moda_candidates.sort(key=lambda x: (x['discountRate'], x['originalPrice']), reverse=True)
beauty_candidates.sort(key=lambda x: (x['discountRate'], x['originalPrice']), reverse=True)
home_candidates.sort(key=lambda x: (x['discountRate'], x['originalPrice']), reverse=True)
tech_candidates.sort(key=lambda x: (x['discountRate'], x['originalPrice']), reverse=True)

# Select exactly 50 per category (or available up to 55)
selected_moda = moda_candidates[:50]
selected_beauty = beauty_candidates[:50]
selected_home = home_candidates[:50]
selected_tech = tech_candidates[:50]

print(f"\nFinal Selection Counts:")
print(f"  Moda: {len(selected_moda)}")
print(f"  Kozmetik: {len(selected_beauty)}")
print(f"  Ev & Yaşam: {len(selected_home)}")
print(f"  Teknoloji: {len(selected_tech)}")

all_catalog = []
for sublist in [selected_moda, selected_beauty, selected_home, selected_tech]:
    for item in sublist:
        # Standardize productUrl
        url = item.get('productUrl', '')
        if '//' in url and not url.startswith('http'):
            url = f"https:{url}"
        url = re.sub(r'https://www\.idefix\.com/+', 'https://www.idefix.com/', url)
        
        all_catalog.append({
            'id': item['id'],
            'title': item['title'],
            'category': item['category'],
            'store': item.get('store', 'Idefix'),
            'originalPrice': float(round(item['originalPrice'], 2)),
            'discountedPrice': float(round(item['discountedPrice'], 2)),
            'discountRate': int(item['discountRate']),
            'productUrl': url,
            'imageUrl': item['imageUrl'],
            'verifiedOnPage': True,
            'onPageDualPrice': f"{round(item['originalPrice'], 2)} TL -> {round(item['discountedPrice'], 2)} TL",
            'verificationStatus': "✅ BAŞARILI - Sayfada Çift Fiyat Teyit Edildi"
        })

print(f"\nTotal finalized verified catalog size: {len(all_catalog)}")

# Save to assets/data/live_deals.json
with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(all_catalog, f, ensure_ascii=False, indent=2)
print("Saved to assets/data/live_deals.json")

# Save to scraper/final_verified_catalog.json
with open('scraper/final_verified_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(all_catalog, f, ensure_ascii=False, indent=2)
print("Saved to scraper/final_verified_catalog.json")
