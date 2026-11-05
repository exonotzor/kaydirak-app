import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

# Test Idefix campaign / outlet pages
urls = [
    'https://www.idefix.com/kampanyalar',
    'https://www.idefix.com/firsatlar',
    'https://www.idefix.com/cok-satanlar',
    'https://www.idefix.com/outlet-c-231394551',
]

for u in urls:
    try:
        r = requests.get(u, headers=headers, verify=False, timeout=6)
        print(u, '-> Status:', r.status_code, 'Len:', len(r.text))
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            links = [a.get('href') for a in soup.find_all('a') if a.get('href') and ('kampanya' in a.get('href') or 'firsat' in a.get('href') or 'indirim' in a.get('href'))]
            print(f"  Found {len(links)} discount/campaign links: {links[:3]}")
    except Exception as e:
        print(u, 'Error:', e)
