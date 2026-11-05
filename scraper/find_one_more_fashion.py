from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Search for Puma or Adidas on Amazon TR
headers = {'Accept-Language': 'tr-TR,tr;q=0.9'}
url = "https://www.amazon.com.tr/s?k=puma+canta"
r = requests.get(url, impersonate='chrome120', timeout=8, verify=False, headers=headers)
asins = re.findall(r'data-asin="([B0-9A-Z]{10})"', r.text)
print(f"Found {len(asins)} ASINs for puma canta")

for asin in asins[:10]:
    if not asin: continue
    p_url = f"https://www.amazon.com.tr/dp/{asin}"
    try:
        pr = requests.get(p_url, impersonate='chrome120', timeout=6, verify=False, headers=headers)
        m = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', pr.text, re.DOTALL)
        t = m.group(1).strip() if m else 'N/A'
        is_out = 'Şu anda mevcut değil' in pr.text
        print(f"ASIN: {asin} | HTTP {pr.status_code} | OUT: {is_out} | Title: {t[:35]}")
    except Exception as e:
        print(f"ASIN {asin} error: {e}")
