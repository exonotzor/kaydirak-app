import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

with open('scraper/amz_deals_script.js', 'r', encoding='utf-8') as f:
    text = f.read()

asins = list(set(re.findall(r'B0[A-Z0-9]{8}', text)))
print(f"Total ASINs: {len(asins)}")

for asin in asins[:8]:
    url = f"https://www.amazon.com.tr/gp/aw/d/{asin}"
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=6)
        print(f"ASIN: {asin} -> Status: {r.status_code}, Len: {len(r.text)}")
        if r.status_code == 200 and len(r.text) > 10000:
            soup = BeautifulSoup(r.text, 'html.parser')
            t = soup.select_one('#title, #productTitle, h1')
            title = t.get_text().strip() if t else 'No Title'
            
            # Check prices
            strikes = re.findall(r'data-a-strike="true"[^>]*>.*?([0-9\.,]+)\s*(?:TL|₺)', r.text, re.DOTALL)
            if not strikes:
                strikes = re.findall(r'basisPrice.*?([0-9\.,]+)\s*(?:TL|₺)', r.text, re.DOTALL)
            sales = re.findall(r'priceToPay.*?([0-9\.,]+)\s*(?:TL|₺)', r.text, re.DOTALL)
            if not sales:
                sales = re.findall(r'apexPriceToPay.*?([0-9\.,]+)\s*(?:TL|₺)', r.text, re.DOTALL)
                
            print(f"  Title: {title[:40]}")
            print(f"  Strikes: {strikes} | Sales: {sales}")
    except Exception as e:
        print(f"ASIN {asin} error: {e}")
