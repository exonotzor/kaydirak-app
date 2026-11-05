import requests
import urllib3
import re
import json
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
    amz_deals = json.load(f)

for deal in amz_deals[:15]:
    short_id = deal.get('shortId')
    try:
        r_go = requests.get(f"https://yaniyo.com/go/{short_id}", headers=headers, verify=False, allow_redirects=False, timeout=5)
        loc = r_go.headers.get('Location', '')
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', loc)
        if not asin_match:
            continue
        asin = asin_match.group(1)
        url = f"https://www.amazon.com.tr/gp/aw/d/{asin}"
        r_page = requests.get(url, headers=headers, verify=False, timeout=6)
        html = r_page.text
        
        # Look for ANY strikethrough text or basisPrice
        strikes = re.findall(r'(?:basisPrice|data-a-strike="true"|a-text-price)[^>]*>([^<]+)', html)
        prices = re.findall(r'(\d+[\.,]\d{2}\s*(?:TL|₺))', html)
        title_match = re.search(r'<title>(.*?)</title>', html)
        t_str = title_match.group(1) if title_match else 'None'
        print(f"ASIN {asin} | Title: {t_str[:30]} | Strikes: {strikes[:2]} | Prices: {prices[:3]}")
    except Exception as e:
        print(f"ASIN error: {e}")
