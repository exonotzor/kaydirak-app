import requests
import re
import urllib3
urllib3.disable_warnings()

headers = {'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)'}
url = 'https://www.hepsiburada.com/bioderma-photoderm-spot-spf50-yuksek-korumali-yuz-ve-vucut-gunes-kremi-150-ml-pm-HB00000IMEJ6'
r = requests.get(url, headers=headers, verify=False, timeout=8)
print("Page length:", len(r.text))
snippets = re.findall(r'.{0,40}(?:TL|₺|fiyat|price).{0,40}', r.text, re.IGNORECASE)
print(f"Found {len(snippets)} snippets")
for s in snippets[:15]:
    print(repr(s.strip()))
