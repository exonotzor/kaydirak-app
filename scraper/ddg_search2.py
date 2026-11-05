import urllib.request
import urllib.parse
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

query = "site:hepsiburada.com maybelline lash sensational sky high maskara"
url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# DuckDuckGo html links
links = re.findall(r'<a class="result__url" href="([^"]+)">', html)
snippets = re.findall(r'<a class="result__snippet[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
print("Links:", links[:5])
for s in snippets[:3]:
    print("Snippet:", re.sub('<[^<]+?>', '', s).strip())
