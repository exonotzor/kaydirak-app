import requests
import urllib3
import json
from bs4 import BeautifulSoup

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

url = 'https://www.idefix.com/kampanyalar/idefix-5te-5-indirimleri-154'
r = requests.get(url, headers=headers, verify=False, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')
if script and script.string:
    data = json.loads(script.string)
    pp = data.get('props', {}).get('pageProps', {})
    banners = pp.get('banners', [])
    for b in banners:
        print("Banner link:", b.get('link'), "Title:", b.get('title'))
    for c in pp.get('listCampaigns', []):
        for ch in c.get('children', []):
            print("Child campaign:", ch.get('name'), "slug:", ch.get('slug'))
