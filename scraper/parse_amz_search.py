import re
from bs4 import BeautifulSoup

with open('scraper/amz_search.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
cards = soup.select('div[data-component-type="s-search-result"]')
print(f"Total Amazon search result cards: {len(cards)}")

found_deals = []
for c in cards:
    asin = c.get('data-asin')
    t = c.select_one('h2 span')
    title = t.get_text().strip() if t else None
    
    # Check for strike price
    strike_elem = c.select_one('.a-text-price .a-offscreen, [data-a-strike="true"] .a-offscreen')
    strike_price = strike_elem.get_text().strip() if strike_elem else None
    
    # Check for sale price
    sale_elem = c.select_one('.a-price .a-offscreen')
    sale_price = sale_elem.get_text().strip() if sale_elem else None
    
    img = c.select_one('img.s-image')
    img_url = img.get('src') if img else None
    
    if strike_price and sale_price and asin and title:
        found_deals.append({
            'asin': asin,
            'title': title,
            'strike': strike_price,
            'sale': sale_price,
            'img': img_url,
            'url': f"https://www.amazon.com.tr/dp/{asin}"
        })

print(f"Amazon products with BOTH strike and sale prices: {len(found_deals)}")
for d in found_deals[:10]:
    print(f"\nASIN: {d['asin']} | {d['sale']} (was {d['strike']})")
    print(f"  Title: {d['title'][:50]}")
    print(f"  URL: {d['url']}")
    print(f"  Img: {d['img']}")
