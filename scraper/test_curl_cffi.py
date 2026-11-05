from curl_cffi import requests
import re

url = "https://www.hepsiburada.com/ara?q=kulaklik"
print("Requesting with curl_cffi impersonate='chrome124', verify=False...")
r = requests.get(url, impersonate="chrome124", verify=False, timeout=10)
print("Status code:", r.status_code)
print("HTML length:", len(r.text))
found_paths = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', r.text)
print("Found PDP links:", len(found_paths))
if found_paths:
    print("Sample:", found_paths[:3])
