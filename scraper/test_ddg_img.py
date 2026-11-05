import urllib.request
import urllib.parse
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://duckduckgo.com/',
}

# 1. Get vqd token
q = "Maybelline Lash Sensational Sky High Maskara hepsiburada"
url = f"https://duckduckgo.com/?q={urllib.parse.quote(q)}"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    page = resp.read().decode('utf-8', errors='ignore')

m = re.search(r'vqd=([0-9-]+)', page) or re.search(r'vqd="([0-9-]+)"', page)
if m:
    vqd = m.group(1)
    print("VQD:", vqd)
    # 2. Query i.js
    img_url = f"https://duckduckgo.com/i.js?l=tr-tr&o=json&q={urllib.parse.quote(q)}&vqd={vqd}&f=,,,&p=1"
    req2 = urllib.request.Request(img_url, headers=headers)
    with urllib.request.urlopen(req2, timeout=10) as resp2:
        data = json.loads(resp2.read().decode('utf-8'))
        print(f"Got {len(data.get('results', []))} image results")
        for res in data.get('results', [])[:3]:
            print("Title:", res.get('title'))
            print("Image:", res.get('image'))
            print("Source:", res.get('url'))
else:
    print("Could not find VQD token")
