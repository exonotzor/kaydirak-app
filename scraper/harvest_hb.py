import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json
import time

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

queries = [
    # Teknoloji
    ('Teknoloji', 'bluetooth kulaklik'),
    ('Teknoloji', 'akilli saat'),
    ('Teknoloji', 'oyuncu mouse'),
    ('Teknoloji', 'powerbank'),
    # Moda
    ('Moda', 'erkek mont'),
    ('Moda', 'spor ayakkabi'),
    ('Moda', 'erkek gomlek'),
    # Ev & Yaşam
    ('Ev & Yaşam', 'tencere seti'),
    ('Ev & Yaşam', 'termos'),
    ('Ev & Yaşam', 'tava'),
    # Kozmetik
    ('Kozmetik', 'gunes kremi'),
    ('Kozmetik', 'parfum'),
    ('Kozmetik', 'nemlendirici krem'),
]

found_hb_deals = []

for cat, q in queries:
    search_url = f"https://www.hepsiburada.com/ara?q={requests.utils.quote(q)}"
    try:
        r = requests.get(search_url, headers=headers, verify=False, timeout=8)
        if r.status_code != 200:
            continue
            
        soup = BeautifulSoup(r.text, 'html.parser')
        links = soup.find_all('a', href=re.compile(r'-p(m)?-[A-Za-z0-9]+'))
        
        seen_urls = set()
        for a in links[:12]:
            href = a.get('href', '')
            if href.startswith('/'):
                href = 'https://www.hepsiburada.com' + href
            if href in seen_urls:
                continue
            seen_urls.add(href)
            
            title = a.get('title') or a.get_text().strip()
            img = a.find('img')
            img_src = img.get('src') if img else None
            
            # Fetch product page to verify on-page dual prices
            try:
                r_pdp = requests.get(href, headers=headers, verify=False, timeout=6)
                if r_pdp.status_code == 200:
                    pdp_soup = BeautifulSoup(r_pdp.text, 'html.parser')
                    h1 = pdp_soup.find('h1')
                    real_title = h1.get_text().strip() if h1 else title
                    
                    # Extract prices
                    # Hepsiburada puts original price and sales price in data-test-id or class
                    # Check prices in text
                    # Look for old price: del, [data-test-id="original-price"], or strikethrough classes
                    old_price_el = pdp_soup.select_one('del, [data-test-id*="del"], [class*="originalPrice"], [class*="oldPrice"], [class*="prevPrice"]')
                    old_p_txt = old_price_el.get_text().strip() if old_price_el else None
                    
                    # Look for sales price
                    sales_price_el = pdp_soup.select_one('[data-test-id*="price"], [class*="finalPrice"]')
                    sales_p_txt = sales_price_el.get_text().strip() if sales_price_el else None
                    
                    # Also check regex for prices if elements not found
                    all_prices = re.findall(r'(\d+[\.,]\d{2}\s*(?:TL|₺))', r_pdp.text)
                    
                    # Clean and parse
                    print(f"[{cat}] HB: {real_title[:35]}")
                    print(f"  Old: {old_p_txt} | Sale: {sales_p_txt} | All: {all_prices[:3]}")
                    
                    # Parse numerical
                    if all_prices and len(all_prices) >= 2:
                        p_vals = []
                        for pt in all_prices[:4]:
                            clean = pt.replace('TL','').replace('₺','').strip().replace('.','').replace(',','.')
                            try:
                                p_vals.append(float(clean))
                            except Exception:
                                pass
                        p_vals = sorted(list(set(p_vals)))
                        if len(p_vals) >= 2 and p_vals[-1] > p_vals[0] and p_vals[0] > 0:
                            p_orig = p_vals[-1]
                            p_sale = p_vals[0]
                            rate = round(((p_orig - p_sale) / p_orig) * 100)
                            if 15 <= rate <= 80:
                                found_hb_deals.append({
                                    'id': f"hb-{len(found_hb_deals)+1}",
                                    'title': real_title,
                                    'category': cat,
                                    'store': 'Hepsiburada',
                                    'originalPrice': p_orig,
                                    'discountedPrice': p_sale,
                                    'discountRate': rate,
                                    'productUrl': href,
                                    'imageUrl': img_src or '',
                                })
                                print(f"  --> VERIFIED DUAL PRICE: {p_orig} TL -> {p_sale} TL (%{rate})")
            except Exception as pe:
                pass
            time.sleep(0.2)
    except Exception as e:
        print(f"Error on {q}: {e}")

print(f"\nTotal verified Hepsiburada deals: {len(found_hb_deals)}")
with open('scraper/hb_verified_deals.json', 'w', encoding='utf-8') as f:
    json.dump(found_hb_deals, f, ensure_ascii=False, indent=2)
