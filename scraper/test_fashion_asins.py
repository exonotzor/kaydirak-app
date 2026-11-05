from curl_cffi import requests
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

asins = [
    'B0HK845RVT', 'B0HFGMGTD2', 'B0HJVKHRQ1', 'B0C2J5XXP2', 'B0C2J86FDJ', 'B07CF6ZH5S',
    'B0FJ8VKBFF', 'B0GH2TZ767', 'B0FXY23156', 'B0HBRXYHXS', 'B0CVRYTP91', 'B0HF7JB792',
    'B0GY7FFMZX', 'B0GVZNK72T'
]

for a in asins:
    url = f"https://www.amazon.com.tr/dp/{a}"
    try:
        r = requests.get(url, impersonate='chrome120', timeout=6, verify=False)
        m = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', r.text, re.DOTALL)
        title = m.group(1).strip() if m else 'N/A'
        is_out = ('Şu anda mevcut değil' in r.text) or ('Temporarily out of stock' in r.text)
        is_404 = ('Sayfa Bulunamadı' in r.text) or ('dogs of amazon' in r.text.lower())
        status = 'OUT' if is_out else ('404' if is_404 else 'OK')
        print(f"{a}: {status} | HTTP {r.status_code} | {title[:45]}")
    except Exception as e:
        print(f"{a}: ERROR {e}")
