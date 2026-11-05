import requests
import urllib3

urllib3.disable_warnings()

uas = [
    ('Android Chrome', 'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.113 Mobile Safari/537.36'),
    ('iOS Safari', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1'),
    ('HB iOS App', 'Hepsiburada/5.35.0 (iPhone; iOS 17.4; Scale/3.00)'),
    ('HB Android 5.30', 'Hepsiburada/5.30.1 (Android 14; Pixel 8)'),
    ('Desktop Edge', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'),
    ('Googlebot', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
]

for name, ua in uas:
    try:
        r = requests.get('https://www.hepsiburada.com/ara?q=kulaklik', headers={'User-Agent': ua, 'Accept-Language': 'tr-TR,tr;q=0.9'}, verify=False, timeout=5)
        print(f"{name}: status {r.status_code}, len {len(r.text)}")
    except Exception as e:
        print(f"{name}: error {e}")
