import openpyxl
import json
import re
import os
import sys
from curl_cffi import requests

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

CATEGORIES = ['Teknoloji', 'Moda', 'Kozmetik', 'Ev & Yaşam']

# Load current Amazon pool
try:
    with open('backend/pool/pool_amazon.json', 'r', encoding='utf-8') as f:
        pool = json.load(f)
except Exception:
    pool = {c: [] for c in CATEGORIES}

existing_asins = set()
for c in CATEGORIES:
    for it in pool[c]:
        m = re.search(r'/dp/([B0-9A-Z]{10})', it.get('productUrl', ''))
        if m:
            existing_asins.add(m.group(1))

print(f"Initial Amazon pool counts: { {c: len(pool[c]) for c in CATEGORIES} }")

# Extract candidate ASINs from Excel
candidates = {c: [] for c in CATEGORIES}
wb = openpyxl.load_workbook('YariFiyatina_Urun_Listesi.xlsx')
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    for row in ws.iter_rows(min_row=2):
        cat = row[1].value
        store = row[2].value
        if store != 'Amazon TR' or cat not in CATEGORIES:
            continue
        title = str(row[3].value or '').strip()
        orig = row[4].value
        disc = row[5].value
        link_cell = row[8]
        img_cell = row[9]
        url = link_cell.hyperlink.target if link_cell.hyperlink else str(link_cell.value or '')
        img = img_cell.hyperlink.target if img_cell.hyperlink else str(img_cell.value or '')
        m = re.search(r'/dp/([B0-9A-Z]{10})', url)
        if not m:
            continue
        asin = m.group(1)
        if asin in existing_asins:
            continue
        try:
            o_val = float(orig)
            d_val = float(disc)
            if o_val <= 0 or d_val <= 0 or d_val >= o_val:
                continue
            rate = int(round((1 - d_val / o_val) * 100))
            if rate < 15:
                continue
        except Exception:
            continue
        if not img.startswith('http'):
            continue
            
        candidates[cat].append({
            'id': f'amz-{asin}',
            'asin': asin,
            'title': title,
            'originalPrice': round(o_val, 2),
            'discountedPrice': round(d_val, 2),
            'discountRate': rate,
            'imageUrl': img,
            'productUrl': f'https://www.amazon.com.tr/dp/{asin}',
            'store': 'Amazon TR',
            'category': cat
        })

print("Candidate counts from Excel:")
for c in CATEGORIES:
    print(f"  {c}: {len(candidates[c])} candidates")

# Check live stock for candidates using curl_cffi
s = requests.Session()
for cat in CATEGORIES:
    target_needed = 40 - len(pool[cat])
    if target_needed <= 0:
        continue
    print(f"\nChecking live stock for {cat} (need {target_needed})...")
    verified_count = 0
    for cand in candidates[cat]:
        if len(pool[cat]) >= 40:
            break
        asin = cand['asin']
        url = cand['productUrl']
        try:
            r = s.get(url, impersonate='chrome120', timeout=10, verify=False)
            html = r.text
            is_404 = 'sayfa bulunamadı' in html.lower() or 'dogs of amazon' in html.lower() or r.status_code == 404
            out_of_stock = 'Şu anda mevcut değil' in html
            if r.status_code == 200 and not is_404 and not out_of_stock:
                pool[cat].append(cand)
                existing_asins.add(asin)
                verified_count += 1
                print(f"  + [OK] {asin} | {cand['title'][:35]} | %{cand['discountRate']}")
            else:
                status = '404' if is_404 else ('OOS' if out_of_stock else f'HTTP_{r.status_code}')
                print(f"  - [{status}] {asin} | {cand['title'][:35]}")
        except Exception as e:
            print(f"  - [ERR] {asin}: {e}")

print("\nFinal Amazon pool sizes:")
for c in CATEGORIES:
    print(f"  {c}: {len(pool[c])}")

with open('backend/pool/pool_amazon.json', 'w', encoding='utf-8') as f:
    json.dump(pool, f, ensure_ascii=False, indent=2)
print("Saved to backend/pool/pool_amazon.json")
