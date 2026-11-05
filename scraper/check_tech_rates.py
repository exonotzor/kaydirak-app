import requests
import urllib3
import json
import re

urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0'}

cats = json.load(open('scraper/idefix_all_categories.json', encoding='utf-8'))
tech_cats = [c for c in cats if any(k in c['url'].lower() for k in ['elektronik', 'bilgisayar', 'telefon', 'gaming', 'oyuncu'])]

all_rates = []
for c in tech_cats[:10]:
    url = f"https://www.idefix.com{c['url']}?sayfa=1"
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=5)
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text)
        if m:
            d = json.loads(m.group(1))
            items = d.get('props',{}).get('pageProps',{}).get('categoryData',{}).get('items',[])
            for it in items:
                for v in it.get('variants', []):
                    p = float(v.get('price') or 0)
                    dp = float(v.get('discountedSalesPrice') or p)
                    if p > 0 and dp < p:
                        rate = round((p - dp) / p * 100)
                        all_rates.append((rate, v.get('name'), p, dp, c['name']))
    except Exception as e:
        pass

print(f"Total discounted items found: {len(all_rates)}")
all_rates.sort(key=lambda x: x[0], reverse=True)
for r in all_rates[:15]:
    print(f"%{r[0]} | {r[3]} TL (was {r[1]} TL) | {r[1][:35]} | Cat: {r[4]}")
