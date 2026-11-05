from curl_cffi import requests
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

url = "https://www.amazon.com.tr/dp/B0CHFFDYBN"
headers = {'Accept-Language': 'tr-TR,tr;q=0.9'}
r = requests.get(url, impersonate='chrome120', timeout=8, verify=False, headers=headers)

print("Status:", r.status_code)
# Search for availability div
m_avail = re.search(r'id=["\']availability["\'][^>]*>(.*?)</div>', r.text, re.DOTALL)
if m_avail:
    print("Availability text:", m_avail.group(1).strip().replace('\n', ' '))
else:
    print("No availability div found!")

# Search where "Şu anda mevcut değil" is
for m in re.finditer(r'Şu anda mevcut değil', r.text):
    start = max(0, m.start() - 100)
    end = min(len(r.text), m.end() + 100)
    print("Snippet:", r.text[start:end].replace('\n', ' '))
