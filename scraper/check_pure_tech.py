import json

with open('scraper/all_tech_verified.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

# exclude outdoor apparel
pure_tech = []
for x in items:
    sub = x['subCategory'].lower()
    title = x['title'].lower()
    if any(k in sub or k in title for k in ['tişört', 'tisort', 'polar', 'ceket', 'mont', 'pantolon', 'şort', 'sort', 'yağmurluk', 'spor giyim']):
        continue
    pure_tech.append(x)

print(f"Total pure tech items: {len(pure_tech)}")
pure_tech.sort(key=lambda x: x['discountRate'], reverse=True)
for x in pure_tech[:35]:
    print(f"%{x['discountRate']} | {x['discountedPrice']} TL (was {x['originalPrice']} TL) | {x['title'][:45]} | {x['subCategory']}")
