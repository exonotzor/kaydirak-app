import json
import urllib.request
import subprocess
from collections import Counter
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('scraper/final_equal_verified_catalog.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

# Let's inspect counts
store_counts = Counter(x['store'] for x in deals)
cat_counts = Counter(x['category'] for x in deals)
print("Store counts:", dict(store_counts))
print("Cat counts:", dict(cat_counts))

# If store counts are 41, 39, 40:
# Let's see which store has 41 and which has 39:
over_store = [s for s, c in store_counts.items() if c > 40]
under_store = [s for s, c in store_counts.items() if c < 40]
print(f"Over: {over_store}, Under: {under_store}")

# We can adjust by checking available verified pool in scraper
# Or let's see which item in over_store can be replaced with an item from under_store of the SAME category:
if over_store and under_store:
    o_s = over_store[0]
    u_s = under_store[0]
    # find category where we can swap
    # load pool
    with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
        tech_pool = json.load(f)
    
    # Let's find an under_store tech item
    u_tech = [x for x in tech_pool if x.get('store') == u_s]
    print(f"Available {u_s} tech items in pool: {len(u_tech)}")
    if u_tech:
        # replace one o_s tech item that is not in top 5
        o_tech_indices = [i for i, x in enumerate(deals) if x['store'] == o_s and x['category'] == 'Teknoloji']
        if len(o_tech_indices) > 2:
            replace_idx = o_tech_indices[-1]
            old_item = deals[replace_idx]
            new_item = u_tech[0]
            deals[replace_idx] = {
                'id': old_item['id'],
                'title': new_item['title'],
                'category': 'Teknoloji',
                'store': u_s,
                'originalPrice': float(new_item['originalPrice']),
                'discountedPrice': float(new_item['discountedPrice']),
                'discountRate': int(new_item['discountRate']),
                'productUrl': new_item['productUrl'],
                'imageUrl': new_item['imageUrl']
            }
            print(f"Swapped [{old_item['store']}] -> [{u_s}]: {new_item['title'][:50]}")

# Now let's do a strict round-robin interleaving so no two consecutive items have the same store
# 3 stores: Amazon TR, Hepsiburada, Idefix
# 40 each
amazon_items = [x for x in deals if x['store'] == 'Amazon TR']
hb_items = [x for x in deals if x['store'] == 'Hepsiburada']
idefix_items = [x for x in deals if x['store'] == 'Idefix']

print(f"Amazon: {len(amazon_items)}, HB: {len(hb_items)}, Idefix: {len(idefix_items)}")

perfect_list = []
for i in range(40):
    perfect_list.append(amazon_items[i])
    perfect_list.append(hb_items[i])
    perfect_list.append(idefix_items[i])

for i, it in enumerate(perfect_list):
    it['id'] = f"deal-{i+1:03d}"

# Check store counts and cat counts
print("Perfect Store Counts:", dict(Counter(x['store'] for x in perfect_list)))
print("Perfect Cat Counts:", dict(Counter(x['category'] for x in perfect_list)))

# Check consecutive collisions
collisions = 0
for i in range(len(perfect_list) - 1):
    if perfect_list[i]['store'] == perfect_list[i+1]['store']:
        collisions += 1
print("Store Collisions:", collisions)

# Save to assets/data/live_deals.json
with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(perfect_list, f, ensure_ascii=False, indent=2)

# Save to scraper/final_equal_verified_catalog.json
with open('scraper/final_equal_verified_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(perfect_list, f, ensure_ascii=False, indent=2)

# Save to scraper/compact_deals.json
with open('scraper/compact_deals.json', 'w', encoding='utf-8') as f:
    json.dump(perfect_list, f, ensure_ascii=False)

# PUT to ExtendsClass bin ccbacbe
url = 'https://extendsclass.com/api/json-storage/bin/ccbacbe'
data = json.dumps(perfect_list, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='PUT')
with urllib.request.urlopen(req) as resp:
    print(f"ExtendsClass PUT status: {resp.status}")

# Upload to Catbox
res = subprocess.run(['curl.exe', '-s', '-F', 'reqtype=fileupload', '-F', 'fileToUpload=@scraper/compact_deals.json', 'https://catbox.moe/user/api.php'], capture_output=True, text=True)
catbox_url = res.stdout.strip()
print(f"New Catbox URL: {catbox_url}")
