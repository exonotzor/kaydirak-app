from curl_cffi import requests

url = "https://www.hepsiburada.com/redmi-buds-6-play-siyah-kulakici-kulaklik-tws-xiaomi-turkiye-garantili-p-HBCV000072PXK3"
targets = ['chrome120', 'safari15_5', 'safari17_0', 'edge101']
for t in targets:
    try:
        r = requests.get(url, impersonate=t, verify=False, timeout=8)
        print(f"Target {t}: status {r.status_code}, len {len(r.text)}")
    except Exception as e:
        print(f"Target {t}: error {e}")
