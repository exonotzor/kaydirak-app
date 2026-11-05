import glob
import json
from collections import Counter

all_deals_by_store = {'Amazon TR': [], 'Hepsiburada': [], 'Idefix': [], 'Other': []}

for f in glob.glob('scraper/*.json'):
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'store' in item:
                        store = item['store']
                        if 'Amazon' in store:
                            all_deals_by_store['Amazon TR'].append(item)
                        elif 'Hepsiburada' in store or 'hepsiburada' in item.get('productUrl', ''):
                            all_deals_by_store['Hepsiburada'].append(item)
                        elif 'Idefix' in store:
                            all_deals_by_store['Idefix'].append(item)
                        else:
                            all_deals_by_store['Other'].append(item)
    except Exception as e:
        pass

for store, items in all_deals_by_store.items():
    urls = set(x.get('productUrl') for x in items if x.get('productUrl'))
    print(f"Store: {store} -> Total raw: {len(items)}, Unique URLs: {len(urls)}")
    cats = Counter(x.get('category') for x in items)
    print(f"  Categories: {dict(cats)}")
