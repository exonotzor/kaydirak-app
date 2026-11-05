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

matches = [m.start() for m in re.finditer(r'"products"\s*:\s*\[', r.text)]
print("Indices of 'products':[ :", matches)
for idx in matches:
    print("--- MATCH AT", idx, "---")
    print(r.text[idx:idx+300])
