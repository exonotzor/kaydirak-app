import json

with open('scraper/amazon_verified_deals.json', 'r', encoding='utf-8') as f:
    amz = json.load(f)

for cat in ['Teknoloji', 'Moda', 'Ev & Yaşam', 'Kozmetik']:
    items = [x for x in amz if x['category'] == cat]
    print(f"=== Amazon {cat} ({len(items)}) ===")
    for it in items[:6]:
        print(f"  %{it['discountRate']} | {it['discountedPrice']} TL (was {it['originalPrice']} TL) | {it['title'][:45]}")
