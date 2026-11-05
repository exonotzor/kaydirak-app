import json
import re

with open('backend/pool/pool_amazon.json', 'r', encoding='utf-8') as f:
    pool = json.load(f)

cleaned = {}
fixed_count = 0

for cat, items in pool.items():
    cleaned[cat] = []
    for it in items:
        img = it.get('imageUrl', '')
        # Clean image URL
        # Strict Amazon image pattern: https://m.media-amazon.com/images/I/[A-Za-z0-9_-]+.jpg
        m = re.search(r'(https://m\.media-amazon\.com/images/I/[A-Za-z0-9%+_-]+(?:\._[A-Za-z0-9_-]+)?\.jpg)', img)
        if m:
            clean_img = m.group(1)
            if clean_img != img:
                fixed_count += 1
                it['imageUrl'] = clean_img
        else:
            # Fallback if image has junk
            if '.js' in img or '<' in img or len(img) > 200:
                m2 = re.search(r'(https://m\.media-amazon\.com/images/I/[A-Za-z0-9%+_-]+)', img)
                if m2:
                    it['imageUrl'] = m2.group(1) + '._AC_UL320_.jpg'
                    fixed_count += 1
                else:
                    it['imageUrl'] = 'https://m.media-amazon.com/images/I/61PPSSbYygL._AC_UL320_.jpg'
                    fixed_count += 1
        
        # Clean title
        it['title'] = it['title'][:120].strip()
        cleaned[cat].append(it)

print(f"Fixed {fixed_count} bloated image URLs in Amazon pool.")

with open('backend/pool/pool_amazon.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

print("Saved clean backend/pool/pool_amazon.json")
