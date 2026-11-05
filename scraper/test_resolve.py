import requests
import urllib3
import json
import re

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

def resolve_amazon_url(short_id):
    try:
        r = requests.get(f"https://yaniyo.com/go/{short_id}", headers=headers, verify=False, allow_redirects=False, timeout=6)
        loc = r.headers.get('Location', '')
        if loc:
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', loc)
            if asin_match:
                return f"https://www.amazon.com.tr/dp/{asin_match.group(1)}"
            return loc.split('?')[0]
    except Exception as e:
        print('Error:', e)
    return f"https://yaniyo.com/go/{short_id}"

with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

realistic = [
    it for it in items
    if 50 <= it.get('discountRate', 0) <= 75 and it.get('discountedPrice', 0) >= 60
]

for it in realistic[:5]:
    url = resolve_amazon_url(it['shortId'])
    print(f"Title: {it['title'][:35]} -> Amazon: {url}")
