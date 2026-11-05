import requests
import urllib3
import re

urllib3.disable_warnings()

# Let's test different headers on Amazon
urls = [
    'https://www.amazon.com.tr/gp/aw/d/B082HS153T',
    'https://www.amazon.com.tr/dp/B082HS153T',
]

user_agents = [
    ('Android Chrome', 'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'),
    ('Desktop Chrome', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'),
    ('Desktop Edge', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'),
]

for name, ua in user_agents:
    try:
        r = requests.get(urls[1], headers={'User-Agent': ua, 'Accept-Language': 'tr-TR,tr;q=0.9'}, verify=False, timeout=6)
        print(f"{name}: status={r.status_code}, len={len(r.text)}, captcha={'Robot' in r.text}")
    except Exception as e:
        print(f"{name}: error={e}")
