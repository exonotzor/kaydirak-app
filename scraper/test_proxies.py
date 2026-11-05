import requests
import urllib3

urllib3.disable_warnings()

# Test public CORS / scrape proxies
proxies_to_test = [
    'https://api.allorigins.win/raw?url=',
    'https://corsproxy.io/?',
]

for p in proxies_to_test:
    target = p + requests.utils.quote('https://www.hepsiburada.com/ara?q=kulaklik')
    try:
        r = requests.get(target, verify=False, timeout=8)
        print(f"Proxy {p[:25]}: status {r.status_code}, len {len(r.text)}")
        if r.status_code == 200 and len(r.text) > 20000:
            print("  SUCCESS!")
    except Exception as e:
        print(f"Proxy {p[:25]}: error {e}")
