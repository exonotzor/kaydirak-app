import requests
import urllib3
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

queries = ['kulaklik', 'laptop', 'telefon', 'parfum', 'saat', 'ayakkabi', 'mont', 'kahve']
for q in queries:
    url = f"https://www.hepsiburada.com/ara?q={q}"
    r = requests.get(url, headers=headers, verify=False, timeout=10)
    links = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', r.text)
    unique_links = list(set(links))
    print(f"Query: {q} | Status: {r.status_code} | HTML len: {len(r.text)} | Unique PDP links: {len(unique_links)}")
