import subprocess
import re
from bs4 import BeautifulSoup
import json
import time
import os

queries = [
    # Teknoloji
    ('Teknoloji', 'https://www.amazon.com.tr/s?k=bluetooth+hoparlor&pct-off=20-'),
    ('Teknoloji', 'https://www.amazon.com.tr/s?k=akilli+bileklik&pct-off=20-'),
    ('Teknoloji', 'https://www.amazon.com.tr/s?k=oyuncu+kulaklik&pct-off=20-'),
    ('Teknoloji', 'https://www.amazon.com.tr/s?k=hizli+sarj+cihazi&pct-off=20-'),
    ('Teknoloji', 'https://www.amazon.com.tr/s?k=mekanik+klavye&pct-off=20-'),

    # Moda
    ('Moda', 'https://www.amazon.com.tr/s?k=erkek+polar&pct-off=20-'),
    ('Moda', 'https://www.amazon.com.tr/s?k=kadin+ceket&pct-off=20-'),
    ('Moda', 'https://www.amazon.com.tr/s?k=sirt+cantasi&pct-off=20-'),
    ('Moda', 'https://www.amazon.com.tr/s?k=erkek+kazak&pct-off=20-'),
    ('Moda', 'https://www.amazon.com.tr/s?k=kadin+sweatshirt&pct-off=20-'),
    ('Moda', 'https://www.amazon.com.tr/s?k=kosu+ayakkabisi&pct-off=20-'),

    # Ev & Yaşam
    ('Ev & Yaşam', 'https://www.amazon.com.tr/s?k=dokum+tava&pct-off=20-'),
    ('Ev & Yaşam', 'https://www.amazon.com.tr/s?k=bicak+seti&pct-off=20-'),
    ('Ev & Yaşam', 'https://www.amazon.com.tr/s?k=kahve+fincani&pct-off=20-'),
    ('Ev & Yaşam', 'https://www.amazon.com.tr/s?k=banyo+havlusu&pct-off=20-'),
    ('Ev & Yaşam', 'https://www.amazon.com.tr/s?k=saklama+kabi&pct-off=20-'),
]

# Load existing
existing = []
if os.path.exists('scraper/amazon_verified_deals.json'):
    with open('scraper/amazon_verified_deals.json', 'r', encoding='utf-8') as f:
        existing = json.load(f)

print(f"Loaded {len(existing)} existing Amazon deals.")
seen_asins = set(x['id'].replace('amz-', '') for x in existing)
seen_titles = set(x['title'][:25].lower() for x in existing)

new_amz = []

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
                
            prefix = title[:25].lower()
            if prefix in seen_titles:
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
                        disc = round(((s_val - p_val) / s_val) * 100)
                        if 15 <= disc <= 85:
                            item = {
                                'id': f"amz-{asin}",
                                'title': title,
                                'category': cat,
                                'store': 'Amazon TR',
                                'originalPrice': s_val,
                                'discountedPrice': p_val,
                                'discountRate': disc,
                                'productUrl': f"https://www.amazon.com.tr/dp/{asin}",
                                'imageUrl': img_url,
                            }
                            seen_asins.add(asin)
                            seen_titles.add(prefix)
                            new_amz.append(item)
                            print(f"  ✅ %{disc} | {p_val} TL (was {s_val} TL) | {title[:35]}")
    except Exception as e:
        print(f"  Error on {url}: {e}")
    time.sleep(1)

total_amz = existing + new_amz
print(f"\nTotal Amazon Deals: {len(total_amz)}")
from collections import Counter
print(Counter(x['category'] for x in total_amz))

with open('scraper/amazon_verified_deals.json', 'w', encoding='utf-8') as f:
    json.dump(total_amz, f, ensure_ascii=False, indent=2)
print("Saved to scraper/amazon_verified_deals.json")
