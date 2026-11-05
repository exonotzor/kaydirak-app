import requests
import urllib3
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)'}
url = 'https://www.hepsiburada.com/ara?q=kulaklik'
r = requests.get(url, headers=headers, verify=False, timeout=8)
soup = BeautifulSoup(r.text, 'html.parser')

for a in soup.find_all('a', href=re.compile(r'-p(m)?-[A-Za-z0-9]+'))[:5]:
    prices = [p.get_text().strip().replace('\n', ' ') for p in a.select('[data-test-id*="price"], [class*="price"], [class*="Price"]')]
    tl_matches = re.findall(r'((?:\d{1,3}\.)*\d+,\d{2}\s*(?:TL|₺))', a.get_text())
    print('Link:', a.get('href')[:50])
    print('  Prices in elem:', prices)
    print('  TL matches:', tl_matches)
