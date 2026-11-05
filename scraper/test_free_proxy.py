import requests
import json

try:
    r = requests.get('https://proxylist.geonode.com/api/proxy-list?limit=10&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps', verify=False, timeout=8)
    data = r.json()
    proxies = [f"{p['protocols'][0]}://{p['ip']}:{p['port']}" for p in data.get('data', [])]
    print("Found proxies:", proxies[:5])
    for px in proxies[:5]:
        try:
            test_r = requests.get('https://www.hepsiburada.com/ara?q=kulaklik', 
                                  headers={'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)'},
                                  proxies={'http': px, 'https': px}, 
                                  verify=False, timeout=6)
            print(f"Proxy {px} -> Status: {test_r.status_code}, Len: {len(test_r.text)}")
            if test_r.status_code == 200:
                print("SUCCESS with proxy!")
                break
        except Exception as pe:
            print(f"Proxy {px} failed: {pe}")
except Exception as e:
    print("Geonode error:", e)
