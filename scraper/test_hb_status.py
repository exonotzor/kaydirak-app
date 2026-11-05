from curl_cffi import requests
import re

try:
    r = requests.get('https://www.hepsiburada.com/ara?q=kulaklik', impersonate='chrome124', verify=False, timeout=10)
    print('Status:', r.status_code, 'Len:', len(r.text))
    pdp_links = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', r.text)
    print('Found PDPs:', len(pdp_links))
except Exception as e:
    print('Error:', e)
