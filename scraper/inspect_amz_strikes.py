import requests
import urllib3
import re
import json
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
    amz_deals = json.load(f)

print(f"Loaded {len(amz_deals)} Amazon candidates.", flush=True)

def check_one(deal):
    short_id = deal.get('shortId')
    try:
        r_go = requests.get(f"https://yaniyo.com/go/{short_id}", headers=headers, verify=False, allow_redirects=False, timeout=4)
        loc = r_go.headers.get('Location', '')
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', loc)
        if not asin_match:
            return None
        asin = asin_match.group(1)
        url = f"https://www.amazon.com.tr/gp/aw/d/{asin}"
        r_page = requests.get(url, headers=headers, verify=False, timeout=5)
        html = r_page.text
        
        # Check for strikethrough or basis price
        strikes = re.findall(r'data-a-strike="true"[^>]*>.*?([0-9\.,]+)\s*(?:TL|₺)', html, re.DOTALL)
        if not strikes:
            strikes = re.findall(r'basisPrice.*?([0-9\.,]+)\s*(?:TL|₺)', html, re.DOTALL)
        if not strikes:
            strikes = re.findall(r'class="[^"]*a-text-price[^"]*"[^>]*>.*?([0-9\.,]+)\s*(?:TL|₺)', html, re.DOTALL)

        sales = re.findall(r'priceToPay.*?([0-9\.,]+)\s*(?:TL|₺)', html, re.DOTALL)
        if not sales:
            sales = re.findall(r'apexPriceToPay.*?([0-9\.,]+)\s*(?:TL|₺)', html, re.DOTALL)
            
        if strikes and sales:
            s_val = float(strikes[0].replace('.', '').replace(',', '.'))
            p_val = float(sales[0].replace('.', '').replace(',', '.'))
            if s_val > p_val:
                rate = round(((s_val - p_val) / s_val) * 100)
                return {
                    'asin': asin,
                    'title': deal.get('title'),
                    'category': deal.get('category'),
                    'strike': s_val,
                    'sale': p_val,
                    'rate': rate,
                    'url': f"https://www.amazon.com.tr/dp/{asin}",
                    'imageUrl': deal.get('imageUrl')
                }
    except Exception:
        pass
    return None

with ThreadPoolExecutor(max_workers=15) as ex:
    results = [r for r in ex.map(check_one, amz_deals[:100]) if r is not None]

print(f"Total Amazon products with verified dual prices in first 100: {len(results)}", flush=True)
for r in results:
    print(f"  %{r['rate']} | {r['sale']} TL (was {r['strike']} TL) | {r['title'][:40]} | Cat: {r['category']}", flush=True)
