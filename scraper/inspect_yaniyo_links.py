import re
from bs4 import BeautifulSoup

content = open(r'C:\Users\suley\.gemini\antigravity\brain\10ce2834-b031-4861-a451-646b5d6f7b5c\.system_generated\steps\1868\content.md', 'r', encoding='utf-8').read()
soup = BeautifulSoup(content, 'html.parser')

links = []
for a in soup.find_all('a', href=True):
    h = a['href']
    if any(k in h for k in ['/firsat/', '/urun/', '/p/', 'ECGH3S23IGA', 'amazon']):
        links.append(h)

print("Found matching links:", len(links))
for l in links[:15]:
    print(" ", l)
