from curl_cffi import requests
import re

url = "https://www.hepsiburada.com/ara?q=parfum"
try:
    r = requests.get(url, impersonate="chrome124", verify=False, timeout=10)
    print("parfum query status:", r.status_code, "Length:", len(r.text))
    found_paths = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', r.text)
    print("Found PDP links:", len(found_paths))
except Exception as e:
    print("Error:", e)
