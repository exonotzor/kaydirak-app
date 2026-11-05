import requests
import json
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

test_cats = [
    ('Teknoloji-Aksesuar', 'https://www.idefix.com/cep-telefonu-aksesuarlari-c-2313374140'),
    ('Teknoloji-Cevre', 'https://www.idefix.com/bilgisayar-bilesenleri-ve-cevre-birimleri-c-2308'),
    ('Teknoloji-Giyilebilir', 'https://www.idefix.com/giyilebilir-teknoloji-c-2309'),
    ('Kozmetik-Parfum', 'https://www.idefix.com/parfum-ve-deodorant-c-4403992550'),
    ('Kozmetik-Kore', 'https://www.idefix.com/kore-kozmetik-l-42012'),
    ('Kozmetik-Cilt', 'https://www.idefix.com/cilt-bakim-c-4401'),
    ('Ev-CokSatan', 'https://www.idefix.com/cok-satanlar-c-11'),
    ('Ev-MutfakGerec', 'https://www.idefix.com/mutfak-gerecleri-c-1101901040'),
    ('Ev-KucukEvAletleri', 'https://www.idefix.com/elektrikli-ev-aletleri-c-2304'),
    ('Moda-Ayakkabi', 'https://www.idefix.com/ayakkabi-c-5503'),
    ('Moda-Valiz', 'https://www.idefix.com/cantalar-valizler-c-5511'),
]

for label, url in test_cats:
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=8)
        if '__NEXT_DATA__' in r.text:
            soup = BeautifulSoup(r.text, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__')
            if script and script.string:
                data = json.loads(script.string)
                pp = data.get('props', {}).get('pageProps', {})
                items = pp.get('categoryData', {}).get('items', []) or pp.get('landingData', {}).get('items', [])
                
                high_deals = []
                for it in items:
                    for v in it.get('variants', []):
                        p = float(v.get('price') or 0)
                        dp = float(v.get('discountedSalesPrice') or p)
                        if p > 0 and dp > 0 and dp < p:
                            rate = round(((p - dp) / p) * 100)
                            if rate >= 50:
                                high_deals.append((v.get('name') or it.get('name'), rate, dp, p, v.get('handleUrl')))
                print(f"[{label}] Items: {len(items)}, Deals >= 50%: {len(high_deals)}")
                for name, rate, dp, p, u in high_deals[:2]:
                    print(f"   -> %{rate} | {dp} TL (was {p} TL) | {str(name)[:35]} | URL: {u}")
    except Exception as e:
        print(f"[{label}] Error: {e}")
