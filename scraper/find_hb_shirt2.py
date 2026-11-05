import urllib.request
import urllib.parse
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

query = "site:hepsiburada.com us polo assn erkek gomlek"
url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    urls = re.findall(r'href="//duckduckgo.com/l/\?uddg=([^"&]+)', html)
    for u in urls:
        decoded = urllib.parse.unquote(u)
        if 'hepsiburada.com' in decoded:
            print("HB link:", decoded)
