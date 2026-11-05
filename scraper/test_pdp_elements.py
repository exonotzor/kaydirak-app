import requests
import urllib3
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = "https://www.hepsiburada.com/hascevher-gastro-30-x-20-cm-derin-tencere-pm-HB000006L9S8"
r = requests.get(url, headers=headers, verify=False, timeout=8)
soup = BeautifulSoup(r.text, 'html.parser')
p_boxes = soup.select('span[data-test-id="variant-box-price"], [data-test-id="default-price"], del, [class*="Price"], [class*="price"]')
for pb in p_boxes[:10]:
    print("Class/tag:", pb.name, pb.get('class'), "Text:", repr(pb.get_text().strip()))

matches = re.findall(r'((?:\d{1,3}\.)*\d+,\d{2}\s*(?:TL|₺))', r.text)
print("Regex price matches:", matches[:10])
