import urllib.request
import urllib.parse
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

queries = [
    "site:hepsiburada.com karaca biogranit 7 parca tencere seti",
    "site:hepsiburada.com logitech g102 lightsync mouse",
    "site:hepsiburada.com us polo assn gomlek",
]

for q in queries:
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            urls = re.findall(r'href="//duckduckgo.com/l/\?uddg=([^"&]+)', html)
            print(f"=== Query: {q} ===")
            for u in urls[:3]:
                decoded = urllib.parse.unquote(u)
                if 'hepsiburada.com' in decoded and '-pm-' in decoded or '-p-' in decoded:
                    print("  ->", decoded)
    except Exception as e:
        print(f"Error for {q}: {e}")
