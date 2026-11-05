import requests
import urllib3
import json
from bs4 import BeautifulSoup

urllib3.disable_warnings()

test_cats = [
    '/kitap-kultur-c-3307',
    '/kadin-giyim-c-5509291910',
    '/erkek-giyim-c-5507240150',
    '/ayakkabi-c-5503',
    '/cantalar-valizler-c-5511',
    '/kozmetik-c-4403',
    '/parfum-ve-deodorant-c-4403992550',
]

real_discount_items = []
for cat in test_cats:
    url = f'https://www.idefix.com{cat}'
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, verify=False, timeout=8)
        soup = BeautifulSoup(r.text, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        if not script:
            continue
        data = json.loads(script.string)
        pp = data.get('props', {}).get('pageProps', {})
        items = pp.get('categoryData', {}).get('items', []) or pp.get('landingData', {}).get('items', [])
        for it in items:
            variants = it.get('variants', [])
            if not variants:
                continue
            v = variants[0]
            price = float(v.get('price') or 0)
            disc_price = float(v.get('discountedSalesPrice') or price)
            if price > disc_price and price > 0:
                rate = round(((price - disc_price) / price) * 100)
                imgs = v.get('images', [])
                img_url = imgs[0].get('src', '').replace('{size}', '600/600/') if imgs else ''
                slug = v.get('handleUrl') or ''
                real_discount_items.append({
                    'title': v.get('name'),
                    'price': price,
                    'disc_price': disc_price,
                    'rate': rate,
                    'img': img_url,
                    'url': f'https://www.idefix.com{slug}',
                    'cat': cat
                })
    except Exception as e:
        print('ERR on', cat, e)

print(f"Found {len(real_discount_items)} items with real discounts.")
real_discount_items.sort(key=lambda x: x['rate'], reverse=True)
for it in real_discount_items[:20]:
    print(f"%{it['rate']} INDIRIM | {it['disc_price']} TL (Eski: {it['price']} TL) | {it['title'][:40]} | {it['url'][:60]}")
