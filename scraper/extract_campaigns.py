import requests
import urllib3
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get('https://www.idefix.com/kampanyalar', headers=headers, verify=False, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

campaigns = []
for a in soup.find_all('a'):
    href = a.get('href', '')
    if '/kampanyalar/' in href:
        title = a.get_text().strip()
        campaigns.append((href, title))

# Deduplicate
seen = set()
unique_camps = []
for h, t in campaigns:
    if h not in seen:
        seen.add(h)
        unique_camps.append((h, t))

print(f"Total unique campaigns: {len(unique_camps)}")
for h, t in unique_camps[:25]:
    print(f"  {h} -> {t[:50]}")
