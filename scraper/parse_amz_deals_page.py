from bs4 import BeautifulSoup
import re
import json

with open('scraper/amz_deals.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
print("Title:", soup.title.get_text() if soup.title else 'No Title')

# Look for deal cards
# In modern Amazon Deals, deals have [data-testid="deal-card"], .DealCard-module, or similar
deal_cards = soup.select('[data-testid*="deal"], [class*="DealCard"], [class*="dealCard"], [class*="Grid-module__grid"]')
print(f"Deal elements found: {len(deal_cards)}")

# Search for any strikethrough or discount tags
discounts = re.findall(r'(%[0-9]+(?:\s*indirim)?)', html, re.IGNORECASE)
print("Discount mentions found:", len(discounts), set(discounts[:10]))

# Search for ASIN links in page
links = soup.find_all('a', href=re.compile(r'/dp/([A-Z0-9]{10})'))
print(f"Direct /dp/ product links found: {len(links)}")

seen_asins = set()
for a in links[:15]:
    href = a.get('href')
    m = re.search(r'/dp/([A-Z0-9]{10})', href)
    if m:
        asin = m.group(1)
        if asin not in seen_asins:
            seen_asins.add(asin)
            print(f"  ASIN: {asin} | Text: {a.get_text().strip()[:40]} | Href: {href[:60]}")
