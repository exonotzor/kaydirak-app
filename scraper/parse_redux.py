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
s = soup.find('script', id='reduxStore')
if s and s.string:
    data = json.loads(s.string)
    print("Redux top keys:", list(data.keys()))
    # Let's inspect subkeys
    for k, v in data.items():
        if isinstance(v, dict):
            print(f"Key '{k}' has subkeys:", list(v.keys())[:10])
            for k2, v2 in v.items():
                if isinstance(v2, list) and len(v2) > 0 and isinstance(v2[0], dict):
                    print(f"Found list of dicts at {k}.{k2} of length {len(v2)}")
                    print("Sample item keys:", list(v2[0].keys())[:15])
