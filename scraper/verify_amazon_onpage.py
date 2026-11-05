import requests
import urllib3
import re
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
    amz_deals = json.load(f)

print(f"Loaded {len(amz_deals)} Amazon candidates.")

def verify_amazon_deal(deal):
    short_id = deal.get('shortId')
    if not short_id:
        return None
        
    # Resolve ASIN
    try:
        r_go = requests.get(f"https://yaniyo.com/go/{short_id}", headers=headers, verify=False, allow_redirects=False, timeout=5)
        loc = r_go.headers.get('Location', '')
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', loc)
        if not asin_match:
            return None
        asin = asin_match.group(1)
        
        # Now fetch Amazon mobile page
        url = f"https://www.amazon.com.tr/gp/aw/d/{asin}"
        r_page = requests.get(url, headers=headers, verify=False, timeout=7)
        if r_page.status_code != 200:
            return None
            
        html = r_page.text
        if len(html) < 15000: # captcha or error
            return None
            
        # Check for visible strikethrough price or basis price on page
        # Amazon puts: <span class="a-price a-text-price" data-a-strike="true"> or basisPrice
        strike_match = re.search(r'data-a-strike="true"[^>]*>.*?([\d\.]+,\d{2})', html)
        if not strike_match:
            strike_match = re.search(r'basisPrice.*?([\d\.]+,\d{2})', html)
            
        # Check for sale price
        sale_match = re.search(r'priceToPay.*?([\d\.]+,\d{2})', html)
        if not sale_match:
            sale_match = re.search(r'apexPriceToPay.*?([\d\.]+,\d{2})', html)
        if not sale_match:
            sale_match = re.search(r'price="([\d\.]+)"', html)
            
        if strike_match and sale_match:
            strike_str = strike_match.group(1).replace('.', '').replace(',', '.')
            sale_str = sale_match.group(1).replace('.', '').replace(',', '.')
            try:
                strike_f = float(strike_str)
                sale_f = float(sale_str)
                if strike_f > sale_f and strike_f > 0:
                    rate = round(((strike_f - sale_f) / strike_f) * 100)
                    if rate >= 50:
                        return {
                            'id': f"amz-{asin}",
                            'title': deal.get('title'),
                            'category': deal.get('category'),
                            'store': 'Amazon TR',
                            'originalPrice': strike_f,
                            'discountedPrice': sale_f,
                            'discountRate': rate,
                            'productUrl': f"https://www.amazon.com.tr/dp/{asin}",
                            'imageUrl': deal.get('imageUrl'),
                            'onPageVerified': True
                        }
            except Exception:
                pass
    except Exception:
        pass
    return None

sample = amz_deals[:40]
print("Testing first 40 Amazon candidates...")
with ThreadPoolExecutor(max_workers=10) as ex:
    results = [r for r in ex.map(verify_amazon_deal, sample) if r is not None]

print(f"Verified on-page strikethrough Amazon deals from sample: {len(results)}")
for r in results:
    print(f"  %{r['discountRate']} | {r['discountedPrice']} TL (was {r['originalPrice']} TL) | {r['title'][:40]}")
