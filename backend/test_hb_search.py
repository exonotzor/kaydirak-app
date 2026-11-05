import requests, json, re, urllib3
urllib3.disable_warnings()

headers = {'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)'}
url = 'https://www.hepsiburada.com/ara?q=parfum'
r = requests.get(url, headers=headers, verify=False, timeout=8)
print('Status code:', r.status_code)
scripts = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)
found = 0
for s in scripts:
    s_clean = s.strip()
    if s_clean.startswith('{') and 'productStat' in s_clean:
        data = json.loads(s_clean)
        prods = data.get('searchState', {}).get('searchProductArray', [])
        found = len(prods)
        if prods:
            print(f"Found {found} products! Sample: {prods[0].get('name')}")
        break
print(f'Total products parsed: {found}')
