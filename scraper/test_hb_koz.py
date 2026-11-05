import requests
import re
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings()

headers = {'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)'}
url = 'https://www.hepsiburada.com/ara?q=gunes+kremi'
r = requests.get(url, headers=headers, verify=False, timeout=8)
found = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', r.text)
print('Found:', len(found))

for u in found[:5]:
    purl = 'https://www.hepsiburada.com' + u.split('?')[0]
    pr = requests.get(purl, headers=headers, verify=False, timeout=8)
    soup = BeautifulSoup(pr.text, 'html.parser')
    h1 = soup.find('h1')
    t = h1.text.strip() if h1 else 'no h1'
    # Look for script tag or price tags
    p_tags = soup.select('span[data-test-id="variant-box-price"], [data-test-id="default-price"], del, [class*="Price"], [class*="price"]')
    prices = [p.get_text().strip() for p in p_tags]
    print('---')
    print('URL:', purl)
    print('Title:', t)
    print('P-Tags:', prices[:6])
