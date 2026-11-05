from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

headers = {'Accept-Language': 'tr-TR,tr;q=0.9'}
url = "https://www.amazon.com.tr/dp/B0DGLSTWRT"
r = requests.get(url, impersonate='chrome120', timeout=8, verify=False, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')
t = soup.find('title')
print("Title tag:", t.get_text() if t else "No title tag")
h1 = soup.find('h1')
print("H1 tag:", h1.get_text().strip() if h1 else "No H1 tag")
