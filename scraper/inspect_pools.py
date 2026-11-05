import json
import os

for fname in ['amazon_verified_deals.json', 'hepsiburada_verified_deals.json', 'yaniyo_amazon_deals.json', 'all_tech_verified.json', 'home_beauty_strict.json']:
    path = os.path.join('scraper', fname)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"{fname}: {len(data)} items")
                    if len(data) > 0 and isinstance(data[0], dict):
                        cats = set(x.get('category', 'None') for x in data)
                        stores = set(x.get('store', 'None') for x in data)
                        print(f"   Cats: {cats}, Stores: {stores}")
                elif isinstance(data, dict):
                    print(f"{fname}: dict with keys {list(data.keys())[:5]}")
            except Exception as e:
                print(f"{fname}: error {e}")
