import requests
import urllib3
import json
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

camps = [
    '/kampanyalar/gamerfix-62',
    '/kampanyalar/elektronik-80',
    '/kampanyalar/idefix-5te-5-indirimleri-154',
    '/kampanyalar/ev-yasam-46',
    '/kampanyalar/kozmetik-kisisel-bakim-31',
    '/kampanyalar/bakim-gunleri-163',
    '/kampanyalar/kahveseverler-126'
]

for c in camps:
    url = f"https://www.idefix.com{c}"
    r = requests.get(url, headers=headers, verify=False, timeout=8)
    soup = BeautifulSoup(r.text, 'html.parser')
    s = soup.find('script', id='__NEXT_DATA__')
    if s and s.string:
        d = json.loads(s.string)
        pp = d.get('props', {}).get('pageProps', {})
        print(f"\nCampaign: {c}")
        print("  PageProps keys:", list(pp.keys()))
        for k in pp.keys():
            val = pp[k]
            if isinstance(val, dict):
                print(f"    {k} keys:", list(val.keys())[:8])
                if 'items' in val:
                    print(f"      items count: {len(val['items'])}")
            elif isinstance(val, list):
                print(f"    {k} list len: {len(val)}")
