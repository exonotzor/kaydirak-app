import requests
import urllib3

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

urls = [
    ("Amazon - Anker Q30", "https://www.amazon.com.tr/dp/B08HMWZBXC"),
    ("Amazon - Sony XM4", "https://www.amazon.com.tr/dp/B09B8W5FW7"),
    ("Amazon - AirPods Pro", "https://www.amazon.com.tr/dp/B08C1W5N87"),
    ("Amazon - iPad", "https://www.amazon.com.tr/dp/B09G96TFF7"),
    ("Amazon - MacBook Air", "https://www.amazon.com.tr/dp/B08N5WRWNW"),
    ("Amazon - Spigen Case", "https://www.amazon.com.tr/dp/B08L5WHFT9"),
    ("Hepsiburada - Xiaomi Watch", "https://www.hepsiburada.com/xiaomi-redmi-watch-3-active-akilli-saat-gri-p-HBCV00004PV142"),
    ("Hepsiburada - Karaca Tencere", "https://www.hepsiburada.com/karaca-biogranit-blackgold-7-parca-tencere-seti-p-HBV00000V0C2R"),
    ("Hepsiburada - US Polo Gomlek", "https://www.hepsiburada.com/us-polo-assn-erkek-dokuma-gomlek-p-HBCV000078P2Q4"),
    ("Hepsiburada - Maybelline Maskara", "https://www.hepsiburada.com/maybelline-new-york-lash-sensational-sky-high-maskara-very-black-siyah-p-HBCV0000085K1Z"),
    ("Hepsiburada - Logitech G102", "https://www.hepsiburada.com/logitech-g-g102-lightsync-rgb-oyuncu-mouse-siyah-p-HBV00000V80EP"),
]

for label, url in urls:
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=8, allow_redirects=True)
        print(f"{label}: status {r.status_code} | final URL: {r.url[:60]}")
    except Exception as e:
        print(f"{label}: ERR {e}")
