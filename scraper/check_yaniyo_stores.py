import requests
import urllib3
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

r = requests.get('https://yaniyo.com', headers=headers, verify=False, timeout=8)
soup = BeautifulSoup(r.text, 'html.parser')
s = soup.find('script', id='__NEXT_DATA__')
if s:
    data = json.loads(s.string)
    print("Yaniyo stores / props:")
    pp = data.get('props', {}).get('pageProps', {})
    print("pageProps keys:", list(pp.keys()))
    if 'stores' in pp:
        print("Stores:", pp['stores'])
