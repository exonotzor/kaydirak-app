import requests
import urllib3
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = 'https://www.hepsiburada.com/redmi-buds-6-play-siyah-kulakici-kulaklik-tws-xiaomi-turkiye-garantili-p-HBCV000072PXK3'
r = requests.get(url, headers=headers, verify=False, timeout=8)
imgs = re.findall(r'https://productimages\.hepsiburada\.net/[^\s"\'<>]+', r.text)
# clean up any trailing chars
clean_imgs = [i.split('?')[0].split('"')[0] for i in imgs if '.jpg' in i or '.png' in i]
print('Found clean images:', len(clean_imgs))
for img in clean_imgs[:5]:
    print(' ', img)
