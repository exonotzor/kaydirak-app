import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

# Test fetching real Amazon product pages to extract the exact real title, image, and price directly from the page HTML
amazon_urls = [
    'https://www.amazon.com.tr/dp/B08HMWZBXC', # Anker Q30
    'https://www.amazon.com.tr/dp/B079ZPMCPV', # Puma
    'https://www.amazon.com.tr/dp/B07P8W9S3D', # Stanley
    'https://www.amazon.com.tr/dp/B08LQWRQ49', # Philips Airfryer
]

for url in amazon_urls:
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        title_el = soup.find('span', id='productTitle')
        title = title_el.get_text(strip=True) if title_el else "TITLE NOT FOUND"
        
        # Image
        img_el = soup.find('img', id='landingImage') or soup.find('img', class_='a-dynamic-image')
        img_url = img_el.get('src') or img_el.get('data-old-hires') if img_el else "IMG NOT FOUND"
        
        # Price
        price_el = soup.select_one('.a-price .a-offscreen') or soup.select_one('#priceblock_ourprice') or soup.select_one('.priceToPay .a-offscreen')
        price = price_el.get_text(strip=True) if price_el else "PRICE NOT FOUND"

        print(f"URL: {url}")
        print(f"  Title: {title[:50]}")
        print(f"  Price: {price}")
        print(f"  Img: {img_url}")
    except Exception as e:
        print(f"ERR on {url}: {e}")
