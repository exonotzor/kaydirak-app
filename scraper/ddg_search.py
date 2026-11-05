import urllib.request
import urllib.parse
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

query = "site:hepsiburada.com \"maybelline new york lash sensational sky high maskara\""
url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"DuckDuckGo returned {len(html)} bytes")
        urls = re.findall(r'href="//duckduckgo.com/l/\?uddg=([^"&]+)', html)
        for u in urls[:5]:
            decoded = urllib.parse.unquote(u)
            print("DDG Link:", decoded)
except Exception as e:
    print(f"DDG Error: {e}")
