import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = "https://www.hepsiburada.com/ara?q=parfum"
r = requests.get(url, headers=headers, verify=False, timeout=10)

# Check if search page contains prices and product cards
soup = BeautifulSoup(r.text, 'html.parser')
# Find JSON data embedded in script tags (e.g. __NEXT_DATA__ or state or product list)
scripts = soup.find_all('script')
for s in scripts:
    if s.string and ('currentPrice' in s.string or 'discount' in s.string or 'strike' in s.string):
        print(f"Found interesting script tag of length {len(s.string)}")
        # let's search for sample product json
        matches = re.findall(r'(\{[^{}]*"price"[^{}]*\})', s.string)
        if matches:
            print("Sample price json:", matches[:2])
        break

# Also check a single PDP page to see what prices it has
pdp_links = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', r.text)
if pdp_links:
    pdp_url = "https://www.hepsiburada.com" + pdp_links[0]
    print("Testing PDP:", pdp_url)
    pdp_r = requests.get(pdp_url, headers=headers, verify=False, timeout=10)
    print("PDP status:", pdp_r.status_code, "Length:", len(pdp_r.text))
    pdp_soup = BeautifulSoup(pdp_r.text, 'html.parser')
    for script in pdp_soup.find_all('script'):
        if script.string and ('originalPrice' in script.string or 'price' in script.string):
            print("Found script in PDP with price keywords!")
            # look for schema.org or JSON-LD
    json_lds = pdp_soup.find_all('script', type='application/ld+json')
    for jld in json_lds:
        print("JSON-LD found:", jld.string[:200] if jld.string else 'None')
