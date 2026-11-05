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
    ('Teknoloji', 'https://www.idefix.com/elektronik-c-23'),
    ('Teknoloji-Aksesuar', 'https://www.idefix.com/cep-telefonu-aksesuarlari-c-2313374140'),
    ('Teknoloji-Kulaklik', 'https://www.idefix.com/kulakliklar-c-230890671'),
    ('Teknoloji-Cevre', 'https://www.idefix.com/bilgisayar-bilesenleri-ve-cevre-birimleri-c-2308'),
    ('Kozmetik', 'https://www.idefix.com/kozmetik-kisisel-bakim-c-44'),
    ('Kozmetik-Parfum', 'https://www.idefix.com/parfum-ve-deodorant-c-4403992550'),
    ('Ev-Yasam', 'https://www.idefix.com/ev-ve-yasam-c-11'),
    ('Ev-Mutfak', 'https://www.idefix.com/mutfak-gerecleri-c-1101901040'),
    ('Moda', 'https://www.idefix.com/ayakkabi-ve-canta-c-5503'),
]

for label, url in test_cats:
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=10)
        if '__NEXT_DATA__' in r.text:
            soup = BeautifulSoup(r.text, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__')
            if script and script.string:
                data = json.loads(script.string)
                pp = data.get('props', {}).get('pageProps', {})
                items = pp.get('categoryData', {}).get('items', []) or pp.get('landingData', {}).get('items', [])
                # Count deals with >= 50% discount
                high_deals = []
                for it in items:
                    orig = float(it.get('price') or 0)
                    disc = float(it.get('discountedSalesPrice') or orig)
                    if orig > 0 and disc > 0 and disc < orig:
                        rate = round(((orig - disc) / orig) * 100)
                        if rate >= 50:
                            high_deals.append((it.get('name'), rate, disc, orig))
                print(f"[{label}] Total items: {len(items)}, Deals >= 50%: {len(high_deals)}")
                for name, rate, disc, orig in high_deals[:2]:
                    print(f"   -> %{rate} | {disc} TL (was {orig} TL) | {name[:40]}")
    except Exception as e:
        print(f"[{label}] Error: {e}")
