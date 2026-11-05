import json

with open('scraper/idefix_strict_onpage.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print('Total strictly verified Idefix items:', len(items))

for cat in ['Moda', 'Kozmetik', 'Ev & Yaşam', 'Teknoloji']:
    sub = [x for x in items if x['category'] == cat]
    print(f"\n=== {cat}: {len(sub)} items ===")
    for x in sub[:5]:
        print(f"  %{x['discountRate']} | {x['discountedPrice']} TL (was {x['originalPrice']} TL) | {x['title'][:40]}")
        print(f"    URL: {x['productUrl']}")
