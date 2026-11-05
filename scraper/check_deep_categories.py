import requests
import urllib3
import json
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

# Inspect specific technology & home subcategories on Idefix
test_urls = [
    ('Teknoloji', '/cep-telefonu-aksesuarlari-c-2313374140'),
    ('Teknoloji', '/kulakliklar-c-2313670940'),
    ('Teknoloji', '/akilli-saatler-c-2313680530'),
    ('Teknoloji', '/klavye-mouse-c-2313680550'),
    ('Ev & Yaşam', '/sofra-mutfak-c-2313680360'),
    ('Ev & Yaşam', '/ev-tekstili-c-2313680390'),
    ('Ev & Yaşam', '/kucuk-ev-aletleri-c-2313680420'),
    ('Ev & Yaşam', '/deterjan-ve-temizlik-urunleri-c-2313933510'),
    ('Kozmetik', '/cilt-bakim-c-2313680450'),
    ('Kozmetik', '/parfum-ve-deodorant-c-2313680440'),
    ('Kozmetik', '/sac-bakim-c-2313680470'),
]

for cat, path in test_urls:
    url = f"https://www.idefix.com{path}?sayfa=1"
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=6)
        if '__NEXT_DATA__' in r.text:
            soup = BeautifulSoup(r.text, 'html.parser')
            s = soup.find('script', id='__NEXT_DATA__')
            if s and s.string:
                d = json.loads(s.string)
                cd = d.get('props', {}).get('pageProps', {}).get('categoryData', {})
                total = cd.get('totalCount')
                items = cd.get('items', [])
                discounts = 0
                for it in items:
                    for v in it.get('variants', []):
                        p = float(v.get('price') or 0)
                        dp = float(v.get('discountedSalesPrice') or p)
                        if p > 0 and dp > 0 and dp < p:
                            rate = round(((p - dp) / p) * 100)
                            if rate >= 50:
                                discounts += 1
                print(f"{cat:12} | {path:35} | Total: {total} | 50%+ in P1: {discounts}")
    except Exception as e:
        print(f"Error on {path}: {e}")
