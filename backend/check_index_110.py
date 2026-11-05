import json

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

for i in range(105, 115):
    d = deals[i]
    print(f"Index {i}: [{d['store']}] [{d['category']}] | {d['title'][:40]}")
