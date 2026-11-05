import requests
import re
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

r = requests.get('https://www.idefix.com/ayakkabi-c-5503', headers=headers, verify=False, timeout=8)
soup = BeautifulSoup(r.text, 'html.parser')
for a in soup.find_all('a', href=True):
    href = a['href']
    if any(k in href for k in ['page', 'sayfa', 'p=']):
        print("Found:", href)
