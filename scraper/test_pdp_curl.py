from curl_cffi import requests
from bs4 import BeautifulSoup
import re

url = "https://www.hepsiburada.com/redmi-buds-6-play-siyah-kulakici-kulaklik-tws-xiaomi-turkiye-garantili-p-HBCV000072PXK3"
r = requests.get(url, impersonate="chrome124", verify=False, timeout=10)
print("PDP status:", r.status_code, "Length:", len(r.text))
soup = BeautifulSoup(r.text, 'html.parser')
h1 = soup.find('h1')
print("Title:", h1.get_text().strip() if h1 else 'None')
p_boxes = soup.select('span[data-test-id="variant-box-price"], [data-test-id="default-price"], del, [class*="Price"], [class*="price"]')
for pb in p_boxes[:5]:
    print("Price box:", pb.get_text().strip())
