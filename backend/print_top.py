import json

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

print(f"Total deals: {len(deals)}")
for i, d in enumerate(deals[:15], 1):
    print(f"{i:02d}. [{d['store']}] [{d['category']}] %{d['discountRate']} | {d['title'][:45]} | {d['discountedPrice']} TL")
