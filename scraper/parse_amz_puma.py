from bs4 import BeautifulSoup
import re

with open('scraper/amz_puma.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
cards = soup.select('div[data-component-type="s-search-result"]')
print(f"Puma cards found: {len(cards)}")

found = []
for c in cards:
    asin = c.get('data-asin')
    t = c.select_one('h2 span')
    title = t.get_text().strip() if t else ''
    
    # Check for strike price
    strike_el = c.select_one('.a-text-price .a-offscreen, [data-a-strike="true"] .a-offscreen')
    strike_txt = strike_el.get_text().strip() if strike_el else None
    
    # Check for sale price
    sale_el = c.select_one('.a-price:not(.a-text-price) .a-offscreen')
    sale_txt = sale_el.get_text().strip() if sale_el else None
    
    img = c.select_one('img.s-image')
    img_url = img.get('src') if img else None
    
    if strike_txt and sale_txt and asin and title:
        m_s = re.search(r'((?:\d{1,3}\.)*\d+,\d{2})', strike_txt)
        m_p = re.search(r'((?:\d{1,3}\.)*\d+,\d{2})', sale_txt)
        if m_s and m_p:
            s_val = float(m_s.group(1).replace('.', '').replace(',', '.'))
            p_val = float(m_p.group(1).replace('.', '').replace(',', '.'))
            if s_val > p_val:
                rate = round(((s_val - p_val) / s_val) * 100)
                found.append({
                    'asin': asin,
                    'title': title,
                    'strike': s_val,
                    'sale': p_val,
                    'rate': rate,
                    'url': f"https://www.amazon.com.tr/dp/{asin}",
                    'img': img_url
                })

print(f"Puma products with verified on-page dual prices: {len(found)}")
for x in found[:10]:
    print(f"  %{x['rate']} | {x['sale']} TL (was {x['strike']} TL) | {x['title'][:40]}")
