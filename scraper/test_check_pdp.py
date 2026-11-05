import requests
import urllib3
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

def check_pdp(url):
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=8)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
        s = soup.find('script', id='reduxStore')
        if not s or not s.string:
            return None
        data = json.loads(s.string)
        prod = data.get('productState', {}).get('product', {})
        name = prod.get('name')
        listings = prod.get('listings', [])
        for l in listings:
            orig = l.get('originalPrice')
            prices = l.get('prices', [])
            val = prices[0].get('value') if prices else None
            disc = l.get('discountRate') or 0
            if orig and val and orig > val:
                rate = round(((orig - val) / orig) * 100)
                if rate >= 15:
                    return {'name': name, 'orig': orig, 'curr': val, 'rate': rate, 'hb_rate': disc}
    except Exception as e:
        pass
    return None

test_urls = [
    "https://www.hepsiburada.com/u-s-polo-assn-erkek-koyu-yesil-uzun-kollu-basic-regular-triko-kazak-50294625-vr033-pm-HBC000072X90M",
    "https://www.hepsiburada.com/hascevher-gastro-30-x-20-cm-derin-tencere-pm-HB000006L9S8",
    "https://www.hepsiburada.com/english-home-florvia-bone-porselen-4-parca-2-kisilik-kahve-fincan-takimi-90-ml-lacivert-pm-HBC000065W0Z0"
]
for u in test_urls:
    print(u)
    print(check_pdp(u))
