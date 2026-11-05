import requests
import urllib3
import re

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = "https://www.hepsiburada.com/ara?q=kulaklik"
r = requests.get(url, headers=headers, verify=False, timeout=10)

idx = r.text.find('"productId":')
if idx != -1:
    print("Found around productId:")
    print(r.text[max(0, idx-100):idx+200])
