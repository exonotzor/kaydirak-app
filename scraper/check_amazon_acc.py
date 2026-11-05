import requests
import urllib3
import re
import json

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

# Filter accessories / audio / cases
candidates = [
    it for it in items
    if any(k in it['title'].lower() for k in ['kılıf', 'kilif', 'kablo', 'şarj', 'kulaklık', 'kulaklik', 'adaptör', 'mouse', 'klavye', 'powerbank'])
]

print(f"Total accessory candidates: {len(candidates)}")

for c in candidates[:15]:
    short_id = c.get('shortId')
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
        
        # Check strike price
        # Amazon writes: <span class="a-price a-text-price" data-a-strike="true"><span class="a-offscreen">1.499,00 TL</span></span>
        strikes = re.findall(r'data-a-strike="true"[^>]*>.*?([\d\.]+,\d{2})', html)
        if not strikes:
            strikes = re.findall(r'basisPrice[^>]*>.*?([\d\.]+,\d{2})', html)
            
        prices = re.findall(r'priceToPay[^>]*>.*?([\d\.]+,\d{2})', html)
        if not prices:
            prices = re.findall(r'apexPriceToPay[^>]*>.*?([\d\.]+,\d{2})', html)
            
        print(f"ASIN: {asin} | {c['title'][:35]} | Strike: {strikes} | Sale: {prices}")
    except Exception as e:
        print('Error:', e)
