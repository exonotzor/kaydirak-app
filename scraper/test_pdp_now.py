import requests
import urllib3
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = "https://www.hepsiburada.com/redmi-buds-6-play-siyah-kulakici-kulaklik-tws-xiaomi-turkiye-garantili-p-HBCV000072PXK3"
r = requests.get(url, headers=headers, verify=False, timeout=8)
print("Status:", r.status_code, "Len:", len(r.text))
if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    h1 = soup.find('h1')
    print("Title:", h1.get_text().strip() if h1 else 'None')
    p_boxes = soup.select('span[data-test-id="variant-box-price"], [data-test-id="default-price"], del, [class*="Price"], [class*="price"]')
    for pb in p_boxes[:5]:
        print("Price box:", pb.get_text().strip())
