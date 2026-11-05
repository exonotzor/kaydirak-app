import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = "https://www.hepsiburada.com/ara?q=kulaklik"
r = requests.get(url, headers=headers, verify=False, timeout=8)

# Find all a tags with -p- or -pm-
soup = BeautifulSoup(r.text, 'html.parser')
links = soup.find_all('a', href=re.compile(r'-p(m)?-[A-Za-z0-9]+'))
print(f"Total product links found: {len(links)}")

seen = set()
for a in links[:15]:
    href = a.get('href', '')
    if href.startswith('/'):
        href = 'https://www.hepsiburada.com' + href
    if href in seen:
        continue
    seen.add(href)
    title = a.get('title') or a.get_text().strip()
    img = a.find('img')
    img_src = img.get('src') if img else None
    print(f"\nTitle: {title[:50]}")
    print(f"  Href: {href}")
    print(f"  Img: {img_src}")
