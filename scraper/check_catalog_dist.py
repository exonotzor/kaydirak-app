import json
from collections import Counter

for filename in ['scraper/amazon_verified_deals.json', 'scraper/idefix_strict_onpage.json', 'scraper/home_beauty_strict.json']:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            counts = Counter(x.get('category', 'Unknown') for x in data)
            print(f"=== {filename} ({len(data)} items) ===")
            print(dict(counts))
    except Exception as e:
        print(f"Error {filename}: {e}")
