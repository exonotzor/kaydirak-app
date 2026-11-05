import requests
import urllib3
import json
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
r = requests.get('https://www.idefix.com/elektronik-c-23', headers=headers, verify=False, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
s = soup.find('script', id='__NEXT_DATA__')
d = json.loads(s.string)
hm = d['props']['pageProps']['headerMenu']['header']

def extract_links(menu):
    links = []
    if isinstance(menu, dict):
        if 'url' in menu and menu['url']:
            links.append((menu.get('name') or menu.get('title'), menu.get('url')))
        for v in menu.values():
            links.extend(extract_links(v))
    elif isinstance(menu, list):
        for item in menu:
            links.extend(extract_links(item))
    return links

all_links = extract_links(hm)
seen_urls = set()
unique_links = []
for name, url in all_links:
    if url not in seen_urls and '-c-' in url or '-l-' in url:
        seen_urls.add(url)
        unique_links.append({'name': name, 'url': url})

print(f"Total unique category links: {len(unique_links)}")

with open('scraper/idefix_all_categories.json', 'w', encoding='utf-8') as f:
    json.dump(unique_links, f, ensure_ascii=False, indent=2)

print("Saved to scraper/idefix_all_categories.json")
