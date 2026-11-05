import urllib.request
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
}

test_urls = [
    "https://www.hepsiburada.com/gunun-firsatlari",
    "https://www.hepsiburada.com/super-fiyat-super-teklif",
    "https://www.amazon.com.tr/deals",
]

for url in test_urls:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"SUCCESS: {url} returned {len(data)} bytes")
    except Exception as e:
        print(f"FAILED: {url} -> {e}")
