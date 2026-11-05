import json
from collections import Counter, defaultdict

# 1. Load Amazon TR verified deals
with open('scraper/amazon_verified_deals.json', 'r', encoding='utf-8') as f:
    amz_all = json.load(f)

# Pick 20 diverse Amazon deals
amz_selected = []
amz_seen_titles = set()
# Target: 5 Teknoloji, 5 Moda, 5 Ev, 5 Kozmetik
amz_cat_targets = {'Teknoloji': 5, 'Moda': 5, 'Ev & Yaşam': 5, 'Kozmetik': 5}
for cat, target in amz_cat_targets.items():
    cat_items = [x for x in amz_all if x['category'] == cat]
    cat_items.sort(key=lambda x: x['discountRate'], reverse=True)
    count = 0
    for it in cat_items:
        prefix = it['title'][:20].lower()
        if prefix in amz_seen_titles:
            continue
        amz_seen_titles.add(prefix)
        it['store'] = 'Amazon TR'
        amz_selected.append(it)
        count += 1
        if count >= target:
            break

print(f"Amazon selected: {len(amz_selected)}")
print(Counter(x['category'] for x in amz_selected))

# 2. Load Hepsiburada verified deals (20 items)
with open('scraper/hepsiburada_verified_deals.json', 'r', encoding='utf-8') as f:
    hb_all = json.load(f)

# Ensure diverse selection of 20
hb_selected = []
hb_seen_titles = set()
for it in hb_all:
    it['store'] = 'Hepsiburada'
    hb_selected.append(it)
hb_selected = hb_selected[:20]

print(f"\nHepsiburada selected: {len(hb_selected)}")
print(Counter(x['category'] for x in hb_selected))

# 3. Load Idefix verified deals
with open('scraper/idefix_strict_onpage.json', 'r', encoding='utf-8') as f:
    idf_all = json.load(f)

with open('scraper/home_beauty_strict.json', 'r', encoding='utf-8') as f:
    idf_hb = json.load(f)

with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    idf_tech = json.load(f)

# Target: 5 Teknoloji, 6 Moda, 5 Ev, 4 Kozmetik = 20
idf_selected = []
idf_seen_titles = set()

# Teknoloji from idf_tech (genuine tech: Casio, Spovan, kulaklik)
tech_pool = [x for x in idf_tech if any(k in x['title'].lower() for k in ['casio', 'spovan', 'kulaklik', 'saat', 'mouse', 'klavye'])]
for t in tech_pool:
    p = t['title'][:20].lower()
    if p not in idf_seen_titles:
        idf_seen_titles.add(p)
        t['store'] = 'Idefix'
        idf_selected.append(t)
        if len([x for x in idf_selected if x['category'] == 'Teknoloji']) >= 5:
            break

# Moda from idf_all
moda_pool = [x for x in idf_all if x.get('category') == 'Moda']
moda_pool.sort(key=lambda x: x.get('discountRate', 0), reverse=True)
for m in moda_pool:
    p = m['title'][:20].lower()
    if p not in idf_seen_titles:
        idf_seen_titles.add(p)
        m['store'] = 'Idefix'
        idf_selected.append(m)
        if len([x for x in idf_selected if x['category'] == 'Moda']) >= 6:
            break

# Ev & Yaşam from idf_hb and idf_all
ev_pool = [x for x in idf_hb + idf_all if x.get('category') == 'Ev & Yaşam']
ev_pool.sort(key=lambda x: x.get('discountRate', 0), reverse=True)
for e in ev_pool:
    p = e['title'][:20].lower()
    if p not in idf_seen_titles:
        idf_seen_titles.add(p)
        e['store'] = 'Idefix'
        idf_selected.append(e)
        if len([x for x in idf_selected if x['category'] == 'Ev & Yaşam']) >= 5:
            break

# Kozmetik from idf_hb
koz_pool = [x for x in idf_hb if x.get('category') == 'Kozmetik']
koz_pool.sort(key=lambda x: x.get('discountRate', 0), reverse=True)
for k in koz_pool:
    p = k['title'][:20].lower()
    if p not in idf_seen_titles:
        idf_seen_titles.add(p)
        k['store'] = 'Idefix'
        idf_selected.append(k)
        if len([x for x in idf_selected if x['category'] == 'Kozmetik']) >= 4:
            break

print(f"\nIdefix selected: {len(idf_selected)}")
print(Counter(x['category'] for x in idf_selected))

# 4. Smart Interleaver
# Balance by rotating store and category
stores = ['Amazon TR', 'Hepsiburada', 'Idefix']
store_queues = {
    'Amazon TR': list(amz_selected),
    'Hepsiburada': list(hb_selected),
    'Idefix': list(idf_selected),
}

interleaved = []
max_len = max(len(q) for q in store_queues.values())
prev_cat = None

for i in range(max_len):
    # rotate store order slightly every round
    shift = i % 3
    round_stores = stores[shift:] + stores[:shift]
    for s in round_stores:
        q = store_queues[s]
        if q:
            # find item with different category than prev_cat if possible
            chosen_idx = 0
            if prev_cat is not None:
                for idx, candidate in enumerate(q):
                    if candidate.get('category') != prev_cat:
                        chosen_idx = idx
                        break
            item = q.pop(chosen_idx)
            interleaved.append(item)
            prev_cat = item.get('category')

print(f"\nTotal interleaved catalog: {len(interleaved)}")
print("Store counts:", Counter(x['store'] for x in interleaved))
print("Category counts:", Counter(x['category'] for x in interleaved))

# Print first 10 items in feed sequence to demonstrate variety
print("\nFirst 10 cards in app sequence:")
for idx, it in enumerate(interleaved[:10]):
    print(f"Card {idx+1}: [{it['store']}] [{it['category']}] %{it['discountRate']} | {it['discountedPrice']} TL (was {it['originalPrice']} TL) | {it['title'][:40]}")

with open('scraper/final_equal_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(interleaved, f, ensure_ascii=False, indent=2)

print("\nSaved to scraper/final_equal_catalog.json")
