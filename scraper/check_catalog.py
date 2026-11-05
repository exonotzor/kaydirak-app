import json

with open(r'c:\Users\suley\OneDrive\AntigravitySync\projects\Discount App\assets\data\live_deals.json', encoding='utf-8') as f:
    deals = json.load(f)

print('Total deals in live_deals.json:', len(deals))
by_store = {}
for d in deals:
    by_store[d['store']] = by_store.get(d['store'], 0) + 1
print('By store:', by_store)

print('\nTop 8 highest discounts:')
for d in deals[:8]:
    print(f"  [{d['store']}] %{d['discountRate']} | {d['discountedPrice']} TL (Eski: {d['originalPrice']} TL) | {d['title'][:40]}")

print('\nAmazon deals:')
for d in deals:
    if 'Amazon' in d['store']:
        print(f"  [{d['store']}] %{d['discountRate']} | {d['discountedPrice']} TL (Eski: {d['originalPrice']} TL) | {d['title'][:40]} | {d['productUrl']}")

print('\nHepsiburada deals:')
for d in deals:
    if 'Hepsiburada' in d['store']:
        print(f"  [{d['store']}] %{d['discountRate']} | {d['discountedPrice']} TL (Eski: {d['originalPrice']} TL) | {d['title'][:40]} | {d['productUrl']}")
