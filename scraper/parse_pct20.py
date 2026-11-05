from bs4 import BeautifulSoup
import re

with open('scraper/amz_pct20.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
cards = soup.select('div[data-component-type="s-search-result"]')
print(f"Cards found: {len(cards)}")

found = 0
for c in cards:
    asin = c.get('data-asin')
    t = c.select_one('h2 span')
    title = t.get_text().strip() if t else ''
    strike_el = c.select_one('.a-text-price .a-offscreen')
    sale_el = c.select_one('.a-price:not(.a-text-price) .a-offscreen')
    if strike_el and sale_el and asin:
        found += 1
        print(f"ASIN {asin}: {sale_el.get_text().strip()} (was {strike_el.get_text().strip()}) | {title[:40]}")

print(f"Total with strike and sale: {found}")
