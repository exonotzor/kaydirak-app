from curl_cffi import requests
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

url = 'https://www.amazon.com.tr/dp/B0GVZNK72T'
try:
    r = requests.get(url, impersonate='chrome120', timeout=10, verify=False)
    print('Status:', r.status_code)
    print('Final URL:', r.url)
    print('Length:', len(r.text))
    if 'productTitle' in r.text:
        m = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', r.text, re.DOTALL)
        if m:
            print('Product Title:', m.group(1).strip())
    elif 'Sayfa Bulunamadı' in r.text or 'dogs of amazon' in r.text.lower() or 'köpek' in r.text.lower():
        print('PAGE NOT FOUND (DOGS / 404)')
    elif 'Robot Değilim' in r.text or 'validateCaptcha' in r.text:
        print('CAPTCHA ENCOUNTERED')
    else:
        print('Snippet:', r.text[:300].replace('\n', ' '))
except Exception as e:
    print('Error:', e)
