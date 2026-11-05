import json

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for i, it in enumerate(d):
    s = json.dumps(it, ensure_ascii=False)
    if len(s) > 1000:
        print(f"Item {i} ({it.get('store')} - {it.get('category')}): {len(s)} chars!")
        for k, v in it.items():
            if len(str(v)) > 150:
                print(f"   {k}: {len(str(v))} chars -> {str(v)[:100]}...")
