import requests
import urllib3

urllib3.disable_warnings()

url = "https://www.hepsiburada.com/logitech-g-g102-lightsync-rgb-oyuncu-mouse-siyah-p-HBV00000V80EP"

uas = [
    ("Googlebot", "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"),
    ("Bingbot", "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"),
    ("Android App", "Hepsiburada/5.32.0 (Android 13; SM-S908B)"),
    ("iOS App", "Hepsiburada/5.32.0 (iPhone; iOS 16.5; Scale/3.00)"),
]

for name, ua in uas:
    try:
        r = requests.get(url, headers={'User-Agent': ua}, verify=False, timeout=6)
        print(f"{name}: status={r.status_code}, len={len(r.text)}, security={'Güvenlik' in r.text or 'Captcha' in r.text}")
    except Exception as e:
        print(f"{name}: error {e}")
