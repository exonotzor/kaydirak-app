import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = "https://www.amazon.com.tr/gp/aw/d/B01M0SYD65"
r = requests.get(url, headers=headers, verify=False, timeout=6)
print("Status:", r.status_code, "Len:", len(r.text))
soup = BeautifulSoup(r.text, 'html.parser')
print("Title tag:", soup.title.get_text() if soup.title else None)
if "Robot Check" in r.text or "bot" in r.text.lower() or "captcha" in r.text.lower():
    print("Detected CAPTCHA / Bot challenge!")
