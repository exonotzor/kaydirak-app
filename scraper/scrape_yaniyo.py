import requests
import urllib3
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

categories = [
    # Teknoloji
    ('Teknoloji', '/elektronik'),
    ('Teknoloji', '/hoparlorler-and-kulakliklar'),
    ('Teknoloji', '/klavye-ve-mouse-seti'),
    ('Teknoloji', '/cep-telefonu-and-aksesuarlari'),
    ('Teknoloji', '/bilgisayarlar'),
    ('Teknoloji', '/monitor'),
    ('Teknoloji', '/akilli-saatler-and-bileklikler'),
    ('Teknoloji', '/tablet-ve-aksesurlari'),
    ('Teknoloji', '/oyun-and-oyun-konsollari'),
    ('Teknoloji', '/foto-and-kamera'),
    ('Teknoloji', '/televizyon'),
    ('Teknoloji', '/sarf-malzemesi'),
    ('Teknoloji', '/fanli-sogutucu'),
    ('Teknoloji', '/yazicilar'),
    
    # Kozmetik
    ('Kozmetik', '/kozmetik'),
    ('Kozmetik', '/kisisel-bakim'),
    ('Kozmetik', '/saglik'),
    
    # Ev & Yaşam
    ('Ev & Yaşam', '/kucuk-ev-aletleri'),
    ('Ev & Yaşam', '/ev-ve-yasam'),
    ('Ev & Yaşam', '/mutfak'),
    ('Ev & Yaşam', '/yapi-market'),
    ('Ev & Yaşam', '/evcil-hayvan-urunleri'),
    
    # Moda
    ('Moda', '/moda-and-giyim'),
]

def fetch_category(cat_name, slug):
    url = f"https://yaniyo.com{slug}?rate=50"
    items = []
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=8)
        soup = BeautifulSoup(r.text, 'html.parser')
        s = soup.find('script', id='__NEXT_DATA__')
        if not s:
            return items
        d = json.loads(s.string)
        prods = d.get('props', {}).get('pageProps', {}).get('initialProducts', [])
        for p in prods:
            name = (p.get('name') or '').strip()
            cur_price = float(p.get('currentPrice') or 0)
            cur_disc = float(p.get('currentDiscount') or 0)
            img = p.get('image') or ''
            short_id = p.get('shortId') or ''
            price_list = p.get('priceList', [])
            
            # calculate orig price
            orig_price = cur_price
            if cur_disc > 0 and cur_disc < 100:
                orig_price = round(cur_price / (1 - cur_disc / 100), 2)
            elif price_list:
                max_price = max(float(x.get('price', 0)) for x in price_list)
                if max_price > cur_price:
                    orig_price = max_price
                    cur_disc = round(((max_price - cur_price) / max_price) * 100)
                    
            if cur_price <= 0 or orig_price <= cur_price or cur_disc < 50:
                continue
                
            if not img or not img.startswith('http'):
                continue
                
            items.append({
                'id': f"amz-{short_id}",
                'title': name,
                'originalPrice': orig_price,
                'discountedPrice': cur_price,
                'discountRate': round(cur_disc),
                'imageUrl': img,
                'shortId': short_id,
                'category': cat_name,
                'store': 'Amazon TR',
            })
    except Exception as e:
        print(f"Error on {slug}: {e}")
    return items

all_items = {}
with ThreadPoolExecutor(max_workers=10) as ex:
    results = ex.map(lambda c: fetch_category(c[0], c[1]), categories)
    for res in results:
        for it in res:
            if it['id'] not in all_items:
                all_items[it['id']] = it

print(f"\nTotal extracted items from Yaniyo (Amazon TR): {len(all_items)}")
from collections import Counter
print(Counter(x['category'] for x in all_items.values()))

with open('scraper/yaniyo_amazon_deals.json', 'w', encoding='utf-8') as f:
    json.dump(list(all_items.values()), f, ensure_ascii=False, indent=2)

print("Saved to scraper/yaniyo_amazon_deals.json")
