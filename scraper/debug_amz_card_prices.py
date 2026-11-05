from bs4 import BeautifulSoup

with open('scraper/amz_search.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
cards = soup.select('div[data-component-type="s-search-result"]')

for idx, c in enumerate(cards[:5]):
    t = c.select_one('h2 span')
    title = t.get_text().strip() if t else 'No Title'
    prices = [p.get_text().strip().replace('\n', ' ') for p in c.select('.a-price, [class*="price"]')]
    print(f"\nCard #{idx}: {title[:40]}")
    print(f"Prices: {prices}")
