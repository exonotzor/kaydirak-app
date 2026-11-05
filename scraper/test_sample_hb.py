import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json
import time

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

test_urls = [
    'https://www.hepsiburada.com/redmi-buds-6-play-siyah-kulakici-kulaklik-tws-xiaomi-turkiye-garantili-p-HBCV000072PXK3',
    'https://www.hepsiburada.com/redmi-buds-6-play-beyaz-kulakici-kulaklik-tws-xiaomi-turkiye-garantili-p-HBCV000072PXK5',
    'https://www.hepsiburada.com/redmi-buds-6-play-mavi-bluetooth-kulaklik-suya-ve-tere-dayanikli-aktif-gurultu-onleme-ozellikli-p-HBCV00007BZNDZ',
    'https://www.hepsiburada.com/xiaomi-redmi-watch-6-gumus-akilli-saat-xiaomi-turkiye-garantili-p-HBCV0000AA03N2',
    'https://www.hepsiburada.com/karaca-biogranit-blackgold-7-parca-tencere-seti-pm-HB00000NGN0E',
]

for u in test_urls:
    try:
        r = requests.get(u, headers=headers, verify=False, timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            h1 = soup.find('h1')
            title = h1.get_text().strip() if h1 else 'No Title'
            
            # Extract prices from variant-box-price or pdp elements
            p_boxes = soup.select('span[data-test-id="variant-box-price"], [data-test-id="default-price"], del')
            prices = []
            for pb in p_boxes:
                txt = pb.get_text().strip()
                m = re.search(r'((?:\d{1,3}\.)*\d+,\d{2})', txt)
                if m:
                    val = float(m.group(1).replace('.', '').replace(',', '.'))
                    prices.append(val)
            
            prices = sorted(list(set(prices)))
            img = soup.select_one('img[data-test-id="product-image"], img[class*="product-image"]')
            img_src = img.get('src') if img else None
            
            print(f"\nTitle: {title[:40]}")
            print(f"Prices found: {prices}")
            print(f"Img: {img_src}")
    except Exception as e:
        print(f"Error {u}: {e}")
