import json

with open('scraper/idefix_strict_onpage.json', 'r', encoding='utf-8') as f:
    idf1 = json.load(f)

with open('scraper/home_beauty_strict.json', 'r', encoding='utf-8') as f:
    idf2 = json.load(f)

with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    idf3 = json.load(f)

all_idf = idf1 + idf2 + [x for x in idf3 if any(k in x['title'].lower() for k in ['kulaklık', 'kulaklik', 'saat', 'mouse', 'klavye', 'powerbank'])]

print(f"Total Idefix pool: {len(all_idf)}")
from collections import Counter
print(Counter(x.get('category') for x in all_idf))

for cat in ['Teknoloji', 'Moda', 'Ev & Yaşam', 'Kozmetik']:
    items = [x for x in all_idf if x.get('category') == cat]
    print(f"\n=== Idefix {cat} ({len(items)}) ===")
    for it in items[:5]:
        print(f"  %{it['discountRate']} | {it['discountedPrice']} TL (was {it['originalPrice']} TL) | {it['title'][:45]}")
