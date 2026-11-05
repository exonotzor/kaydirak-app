import json
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

with open('scraper/idefix_all_categories.json', 'r', encoding='utf-8') as f:
    cats = json.load(f)

# Find categories containing keywords
tech_cats = [c for c in cats if any(w in c['url'].lower() for w in ['elektronik', 'telefon', 'bilgisayar', 'tablet', 'gaming', 'kulaklik', 'mouse', 'klavye', 'sarj', 'kablo', 'giyilebilir', 'tv', 'ses', 'kamera', 'konsol'])]
beauty_cats = [c for c in cats if any(w in c['url'].lower() for w in ['kozmetik', 'parfum', 'cilt', 'makyaj', 'sac', 'kisisel'])]
home_cats = [c for c in cats if any(w in c['url'].lower() for w in ['ev-', 'mutfak', 'sofra', 'tekstil', 'banyo', 'aydinlatma', 'mobilya', 'dekorasyon', 'yasam', 'temizlik', 'gerecleri', 'aletleri'])]

print(f"Tech categories in menu: {len(tech_cats)}")
print(f"Beauty categories in menu: {len(beauty_cats)}")
print(f"Home categories in menu: {len(home_cats)}")

def scan_group(group_name, group_cats):
    print(f"\n--- Scanning {group_name} ---")
    found = []
    for c in group_cats[:25]:
        for p in range(1, 4):
            url = f"https://www.idefix.com{c['url']}?sayfa={p}"
            try:
                r = requests.get(url, headers=headers, verify=False, timeout=6)
                if '__NEXT_DATA__' not in r.text:
                    continue
                soup = BeautifulSoup(r.text, 'html.parser')
                s = soup.find('script', id='__NEXT_DATA__')
                if not s or not s.string:
                    continue
                d = json.loads(s.string)
                items = d.get('props', {}).get('pageProps', {}).get('categoryData', {}).get('items', [])
                if not items:
                    continue
                for it in items:
                    for v in it.get('variants', []):
                        p_orig = float(v.get('price') or 0)
                        p_disc = float(v.get('discountedSalesPrice') or p_orig)
                        if p_orig > 0 and p_disc > 0 and p_disc < p_orig:
                            rate = round(((p_orig - p_disc) / p_orig) * 100)
                            if rate >= 50:
                                found.append({
                                    'title': v.get('name'),
                                    'rate': rate,
                                    'orig': p_orig,
                                    'disc': p_disc,
                                    'url': v.get('handleUrl'),
                                    'cat': c['name']
                                })
            except Exception:
                pass
    print(f"{group_name}: Found {len(found)} items with >= 50% discount.")
    for it in found[:5]:
        print(f"  %{it['rate']} | {it['disc']} TL (was {it['orig']} TL) | {str(it['title'])[:40]} ({it['cat']})")

scan_group("Teknoloji", tech_cats)
scan_group("Kozmetik", beauty_cats)
scan_group("Ev & Yaşam", home_cats)
