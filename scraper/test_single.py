import requests
import urllib3
import re

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

q = 'bluetooth kulaklik'
search_url = f"https://www.hepsiburada.com/ara?q={requests.utils.quote(q)}"
print("Fetching:", search_url)
try:
    r = requests.get(search_url, headers=headers, verify=False, timeout=8)
    print("Status:", r.status_code, "Length:", len(r.text))
    found_paths = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', r.text)
    print("Found paths:", len(found_paths))
    if found_paths:
        print("Sample path:", found_paths[0])
except Exception as e:
    print("Error:", e)
