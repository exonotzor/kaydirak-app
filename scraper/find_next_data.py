import requests
import urllib3
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = "https://www.hepsiburada.com/ara?q=kulaklik"
r = requests.get(url, headers=headers, verify=False, timeout=10)

soup = BeautifulSoup(r.text, 'html.parser')
for s in soup.find_all('script'):
    sid = s.get('id', '')
    stype = s.get('type', '')
    if sid or stype:
        print(f"Script tag: id='{sid}', type='{stype}', len={len(s.string or '')}")
        if sid == '__NEXT_DATA__' or 'json' in stype:
            try:
                data = json.loads(s.string)
                print("JSON keys:", list(data.keys()))
                # Let's inspect deep keys
                if 'props' in data:
                    print("Props keys:", list(data['props'].keys()))
                    page_props = data['props'].get('pageProps', {})
                    print("pageProps keys:", list(page_props.keys()))
            except Exception as e:
                print("Error parsing json script:", e)
