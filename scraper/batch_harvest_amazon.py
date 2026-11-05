import subprocess
import re
from bs4 import BeautifulSoup
import json
import time

queries = [
    # Teknoloji
    ('Teknoloji', 'https://www.amazon.com.tr/s?k=kulaklik&pct-off=20-'),
    ('Teknoloji', 'https://www.amazon.com.tr/s?k=mouse+klavye&pct-off=20-'),
    ('Teknoloji', 'https://www.amazon.com.tr/s?k=powerbank&pct-off=20-'),
    ('Teknoloji', 'https://www.amazon.com.tr/s?k=akilli+saat&pct-off=20-'),
    ('Teknoloji', 'https://www.amazon.com.tr/s?k=hoparlor&pct-off=20-'),
    
    # Moda
    ('Moda', 'https://www.amazon.com.tr/s?k=erkek+mont&pct-off=20-'),
    ('Moda', 'https://www.amazon.com.tr/s?k=kadin+mont&pct-off=20-'),
    ('Moda', 'https://www.amazon.com.tr/s?k=spor+ayakkabi&pct-off=20-'),
    ('Moda', 'https://www.amazon.com.tr/s?k=sweatshirt&pct-off=20-'),
    ('Moda', 'https://www.amazon.com.tr/s?k=gomlek&pct-off=20-'),
    
    # Ev & Yaşam
    ('Ev & Yaşam', 'https://www.amazon.com.tr/s?k=tencere+seti&pct-off=20-'),
    ('Ev & Yaşam', 'https://www.amazon.com.tr/s?k=termos&pct-off=20-'),
    ('Ev & Yaşam', 'https://www.amazon.com.tr/s?k=tava&pct-off=20-'),
    ('Ev & Yaşam', 'https://www.amazon.com.tr/s?k=nevresim&pct-off=20-'),
    
    # Kozmetik
    ('Kozmetik', 'https://www.amazon.com.tr/s?k=krem&pct-off=20-'),
    ('Kozmetik', 'https://www.amazon.com.tr/s?k=parfum&pct-off=20-'),
    ('Kozmetik', 'https://www.amazon.com.tr/s?k=serum&pct-off=20-'),
    ('Kozmetik', 'https://www.amazon.com.tr/s?k=gunes+kremi&pct-off=20-'),
]

all_amz_deals = []
seen_asins = set()

for cat, url in queries:
    print(f"\nScanning Amazon: {cat} -> {url}")
    cmd = f'"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --headless=new --disable-gpu --dump-dom "{url}"'
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        html = out.decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.select('div[data-component-type="s-search-result"]')
        print(f"  Found {len(cards)} search result cards.")
        
        for c in cards:
            asin = c.get('data-asin')
            if not asin or asin in seen_asins:
                continue
                
            t = c.select_one('h2 span')
            title = t.get_text().strip() if t else ''
            if not title or len(title) < 5:
                continue
                
            strike_el = c.select_one('.a-text-price .a-offscreen')
            sale_el = c.select_one('.a-price:not(.a-text-price) .a-offscreen')
            img_el = c.select_one('img.s-image')
            img_url = img_el.get('src') if img_el else ''
            
            if strike_el and sale_el and img_url:
                s_txt = strike_el.get_text().strip()
                p_txt = sale_el.get_text().strip()
                
                m_s = re.search(r'((?:\d{1,3}\.)*\d+,\d{2})', s_txt)
                m_p = re.search(r'((?:\d{1,3}\.)*\d+,\d{2})', p_txt)
                if m_s and m_p:
                    s_val = float(m_s.group(1).replace('.', '').replace(',', '.'))
                    p_val = float(m_p.group(1).replace('.', '').replace(',', '.'))
                    if s_val > p_val and p_val > 0:
                        rate = round(((s_val - p_val) / s_val) * 100)
                        if 15 <= rate <= 80:
                            seen_asins.add(asin)
                            deal = {
                                'id': f"amz-{asin}",
                                'asin': asin,
                                'title': title,
                                'category': cat,
                                'store': 'Amazon TR',
                                'originalPrice': s_val,
                                'discountedPrice': p_val,
                                'discountRate': rate,
                                'productUrl': f"https://www.amazon.com.tr/dp/{asin}",
                                'imageUrl': img_url,
                            }
                            all_amz_deals.append(deal)
                            print(f"    + [%{rate}] {p_val} TL (was {s_val} TL) | {title[:40]}")
    except Exception as e:
        print(f"Error on {url}: {e}")
    time.sleep(0.5)

print(f"\nTotal verified Amazon TR deals harvested: {len(all_amz_deals)}")
from collections import Counter
print(Counter(x['category'] for x in all_amz_deals))

with open('scraper/amazon_verified_deals.json', 'w', encoding='utf-8') as f:
    json.dump(all_amz_deals, f, ensure_ascii=False, indent=2)
print("Saved to scraper/amazon_verified_deals.json")
