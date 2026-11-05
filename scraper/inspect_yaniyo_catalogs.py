import re
from bs4 import BeautifulSoup

content = open(r'C:\Users\suley\.gemini\antigravity\brain\10ce2834-b031-4861-a451-646b5d6f7b5c\.system_generated\steps\1868\content.md', 'r', encoding='utf-8').read()
soup = BeautifulSoup(content, 'html.parser')

cats = []
for a in soup.find_all('a', href=True):
    h = a['href']
    t = a.get_text(strip=True)
    if h.startswith('/') and len(h) > 1 and not h.startswith('/go/') and not h.startswith('/auth'):
        cats.append((t, h))

print(f"Total internal links: {len(cats)}")
for t, h in set(cats):
    print(f"  {t:30} -> {h}")
