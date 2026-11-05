import requests
import urllib3
from PIL import Image
from io import BytesIO

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

products = [
    {
        "store": "Amazon TR",
        "title": "Anker Soundcore Life Q30 Bluetooth Kulaklık",
        "url": "https://www.amazon.com.tr/dp/B08HMWZBXC",
        "img": "https://images-na.ssl-images-amazon.com/images/P/B08HMWZBXC.01._SCLZZZZZZZ_SX500_.jpg"
    },
    {
        "store": "Amazon TR",
        "title": "Sony WH-1000XM4 Kablosuz Kulaklık",
        "url": "https://www.amazon.com.tr/dp/B09B8W5FW7",
        "img": "https://images-na.ssl-images-amazon.com/images/P/B09B8W5FW7.01._SCLZZZZZZZ_SX500_.jpg"
    },
    {
        "store": "Amazon TR",
        "title": "Apple AirPods Pro Bluetooth Kulaklık",
        "url": "https://www.amazon.com.tr/dp/B08C1W5N87",
        "img": "https://images-na.ssl-images-amazon.com/images/P/B08C1W5N87.01._SCLZZZZZZZ_SX500_.jpg"
    },
    {
        "store": "Amazon TR",
        "title": "Apple iPad 10.2 inç Wi-Fi 64GB",
        "url": "https://www.amazon.com.tr/dp/B09G96TFF7",
        "img": "https://images-na.ssl-images-amazon.com/images/P/B09G96TFF7.01._SCLZZZZZZZ_SX500_.jpg"
    },
    {
        "store": "Amazon TR",
        "title": "Apple MacBook Air 13 inç M1",
        "url": "https://www.amazon.com.tr/dp/B08N5WRWNW",
        "img": "https://images-na.ssl-images-amazon.com/images/P/B08N5WRWNW.01._SCLZZZZZZZ_SX500_.jpg"
    },
    {
        "store": "Amazon TR",
        "title": "Spigen iPhone Crystal Clear Kılıf",
        "url": "https://www.amazon.com.tr/dp/B08L5WHFT9",
        "img": "https://images-na.ssl-images-amazon.com/images/P/B08L5WHFT9.01._SCLZZZZZZZ_SX500_.jpg"
    },
    {
        "store": "Hepsiburada",
        "title": "Xiaomi Redmi Watch 3 Active Akıllı Saat",
        "url": "https://www.hepsiburada.com/xiaomi-redmi-watch-3-active-akilli-saat-gri-p-HBCV00004PV142",
        "img": "https://productimages.hepsiburada.net/s/434/550/110000466314841.jpg"
    },
    {
        "store": "Hepsiburada",
        "title": "Karaca Biogranit Blackgold 7 Parça Tencere Seti",
        "url": "https://www.hepsiburada.com/karaca-biogranit-blackgold-7-parca-tencere-seti-p-HBV00000V0C2R",
        "img": "https://productimages.hepsiburada.net/s/45/550/10834371510322.jpg"
    },
    {
        "store": "Hepsiburada",
        "title": "U.S. Polo Assn. Erkek Gömlek",
        "url": "https://www.hepsiburada.com/us-polo-assn-erkek-dokuma-gomlek-p-HBCV000078P2Q4",
        "img": "https://productimages.hepsiburada.net/s/774/550/110000962386345.jpg"
    },
    {
        "store": "Hepsiburada",
        "title": "Maybelline New York Sky High Maskara",
        "url": "https://www.hepsiburada.com/maybelline-new-york-lash-sensational-sky-high-maskara-very-black-siyah-p-HBCV0000085K1Z",
        "img": "https://productimages.hepsiburada.net/s/54/550/11181829390386.jpg"
    },
    {
        "store": "Hepsiburada",
        "title": "Logitech G102 Lightsync RGB Mouse",
        "url": "https://www.hepsiburada.com/logitech-g-g102-lightsync-rgb-oyuncu-mouse-siyah-p-HBV00000V80EP",
        "img": "https://productimages.hepsiburada.net/s/40/550/10660604870706.jpg"
    }
]

for p in products:
    try:
        r_img = requests.get(p['img'], verify=False, timeout=5)
        im = Image.open(BytesIO(r_img.content))
        print(f"[{p['store']}] {p['title']} -> Image OK ({im.size})")
    except Exception as e:
        print(f"[{p['store']}] {p['title']} -> Image ERR: {e}")
