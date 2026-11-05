import urllib.request
import re
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
}

urls = [
    ("U.S. Polo Gömlek", "https://productimages.hepsiburada.net/s/774/550/110000962386345.jpg"),
    ("Karaca Tencere", "https://productimages.hepsiburada.net/s/45/550/10834371510322.jpg"),
    ("Maybelline Maskara", "https://productimages.hepsiburada.net/s/54/550/11181829390386.jpg"),
    ("Logitech G102", "https://productimages.hepsiburada.net/s/40/550/10660604870706.jpg"),
    ("Stanley Cookset", "https://m.media-amazon.com/images/I/61LKfn0LGZL.jpg"),
    ("Anthony Jackson Valiz", "https://m.media-amazon.com/images/I/81LG8GPgnOL.jpg"),
    ("Spigen Clear Case", "https://images-na.ssl-images-amazon.com/images/P/B08L5WHFT9.01._SCLZZZZZZZ_SX600_.jpg"),
]

os.makedirs("scraper/temp_check", exist_ok=True)
for name, url in urls:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name)
            out_file = f"scraper/temp_check/{clean_name}.jpg"
            with open(out_file, "wb") as f:
                f.write(content)
            print(f"Downloaded {name}: {len(content)} bytes -> {out_file}")
    except Exception as e:
        print(f"Error {name}: {e}")
