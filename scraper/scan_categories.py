import requests
import urllib3
import json
from bs4 import BeautifulSoup

urllib3.disable_warnings()

test_urls = {
    'Teknoloji': [
        'https://www.idefix.com/elektronik-c-23',
        'https://www.idefix.com/cep-telefonu-aksesuarlari-c-2313374140',
        'https://www.idefix.com/kulakliklar-c-230890671',
        'https://www.idefix.com/bilgisayar-bilesenleri-ve-cevre-birimleri-c-2308',
        'https://www.idefix.com/gaming-c-230861',
        'https://www.idefix.com/akilli-saatler-c-2309902640',
        'https://www.idefix.com/sarj-cihazlari-ve-kablolar-c-2313374140900130'
    ],
    'Kozmetik': [
        'https://www.idefix.com/kozmetik-kisisel-bakim-c-44',
        'https://www.idefix.com/parfum-ve-deodorant-c-4403992550',
        'https://www.idefix.com/cilt-bakim-c-4401',
        'https://www.idefix.com/makyaj-c-4402',
        'https://www.idefix.com/sac-bakim-c-4404'
    ],
    'Ev & Yasam': [
        'https://www.idefix.com/ev-ve-yasam-c-11',
        'https://www.idefix.com/mutfak-gerecleri-c-1101901040',
        'https://www.idefix.com/ev-tekstili-c-1102',
        'https://www.idefix.com/sofra-servis-sunum-c-1101',
        'https://www.idefix.com/aydinlatma-c-1104',
        'https://www.idefix.com/banyo-aksesuarlari-c-1105'
    ],
    'Moda': [
        'https://www.idefix.com/ayakkabi-c-5503',
        'https://www.idefix.com/cantalar-valizler-c-5511',
        'https://www.idefix.com/kadin-giyim-c-5509291910',
        'https://www.idefix.com/erkek-giyim-c-5507240150',
        'https://www.idefix.com/saat-ve-aksesuar-c-5505'
    ]
}

for cat, urls in test_urls.items():
    for u in urls:
        slug = u.split('/')[-1]
        try:
            r = requests.get(u, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=8)
            if '__NEXT_DATA__' in r.text:
                soup = BeautifulSoup(r.text, 'html.parser')
                s = soup.find('script', id='__NEXT_DATA__')
                d = json.loads(s.string)
                cd = d.get('props', {}).get('pageProps', {}).get('categoryData', {})
                items = cd.get('items', [])
                total = cd.get('totalCount', 0)
                deals_50 = 0
                for it in items:
                    for v in it.get('variants', []):
                        p = float(v.get('price') or 0)
                        dp = float(v.get('discountedSalesPrice') or p)
                        if p > 0 and dp > 0 and dp < p:
                            if round(((p - dp) / p) * 100) >= 50:
                                deals_50 += 1
                print(f"{cat:12} | {slug:40} | total: {total:6} | p1 items: {len(items):2} | >=50%: {deals_50}")
            else:
                print(f"{cat:12} | {slug:40} | NO NEXT_DATA (status {r.status_code})")
        except Exception as e:
            print(f"{cat:12} | {slug:40} | ERR: {e}")
