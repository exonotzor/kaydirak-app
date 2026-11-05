import requests
import urllib3

urllib3.disable_warnings()

r = requests.post('https://dpaste.org/api/', data={'content': '{"status": "ok"}', 'format': 'url', 'expiry_days': 365}, verify=False, timeout=8)
print('dpaste status:', r.status_code)
dpaste_url = r.text.strip()
print('dpaste url:', dpaste_url)

raw_url = dpaste_url + '/raw'
g = requests.get(raw_url, verify=False, timeout=8)
print('dpaste raw:', g.status_code, g.text)
