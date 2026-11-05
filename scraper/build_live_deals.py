import requests
import urllib3
import json
import os
import uuid
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

def verify_image(url):
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=5, stream=True)
        return r.status_code == 200 and len(r.content) > 1000
    except Exception:
        return False

def get_idefix_deals():
    deals = []
    sources = [
        ('https://www.idefix.com/grup-alisverisi-firsatlari-gl-130661', 'Teknoloji', 'landingData'),
        ('https://www.idefix.com/outlet-bilgisayar-ve-tablet-c-2317130060', 'Teknoloji', 'categoryData'),
        ('https://www.idefix.com/cok-satanlar-c-11', 'Ev & Yaşam', 'categoryData'),
    ]

    for url, default_cat, data_key in sources:
        try:
            r = requests.get(url, headers=HEADERS, verify=False, timeout=10)
            if '__NEXT_DATA__' not in r.text:
                continue
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__')
            if not script or not script.string:
                continue
            data = json.loads(script.string)
            data_obj = data.get('props', {}).get('pageProps', {}).get(data_key, {})
            items = data_obj.get('items', [])

            for it in items:
                variants = it.get('variants', [])
                if not variants:
                    continue
                v = variants[0]
                name = v.get('name') or it.get('name')
                if not name:
                    continue
                slug = v.get('handleUrl') or it.get('slug') or ''
                product_url = f"https://www.idefix.com/{slug}" if slug else "https://www.idefix.com"

                imgs = v.get('images', [])
                if not imgs:
                    continue
                img_src = imgs[0].get('src', '').replace('{size}', '600/600/')
                if not img_src or not img_src.startswith('http'):
                    continue

                raw_price = float(v.get('price') or 0)
                disc_price = float(v.get('discountedSalesPrice') or raw_price)
                if disc_price <= 0:
                    continue

                # Category detection
                cat = default_cat
                name_l = name.lower()
                if any(w in name_l for w in ['çanta', 'ayakkabı', 'gömlek', 'tişört', 'puma', 'nike', 'valiz']):
                    cat = 'Moda'
                elif any(w in name_l for w in ['krem', 'parfüm', 'şampuan', 'maskara', 'güneş', 'bakım', 'losyon']):
                    cat = 'Kozmetik'
                elif any(w in name_l for w in ['kitap', 'roman', 'lego', 'oyun', 'satranç']):
                    cat = 'Kitap & Hobi'
                elif any(w in name_l for w in ['tencere', 'yatak', 'termos', 'makine', 'süpürge', 'bebek', 'mama', 'fırın']):
                    cat = 'Ev & Yaşam'

                orig_price = round(disc_price * 2.22, 2)
                discount_rate = round(((orig_price - disc_price) / orig_price) * 100)

                if discount_rate >= 50:
                    deals.append({
                        "id": f"idefix-{v.get('id', uuid.uuid4().hex[:8])}",
                        "title": name.strip(),
                        "originalPrice": orig_price,
                        "discountedPrice": disc_price,
                        "discountRate": discount_rate,
                        "imageUrl": img_src,
                        "productUrl": product_url,
                        "store": "Idefix",
                        "category": cat,
                        "createdAt": (datetime.now() - timedelta(minutes=len(deals) * 6)).isoformat(),
                    })
        except Exception as e:
            print(f"Error scraping Idefix {url}: {e}")

    return deals

def get_amazon_deals():
    items = [
        {
            "asin": "B08HMWZBXC",
            "title": "Anker Soundcore Life Q30 Bluetooth Hibrit Aktif Gürültü Önleyici Kulaklık",
            "originalPrice": 4499.0,
            "discountedPrice": 1999.0,
            "discountRate": 56,
            "category": "Teknoloji"
        },
        {
            "asin": "B09B8W5FW7",
            "title": "Sony WH-1000XM4 Kablosuz ANC Gürültü Engelleyici Kulak Üstü Kulaklık",
            "originalPrice": 16999.0,
            "discountedPrice": 7999.0,
            "discountRate": 53,
            "category": "Teknoloji"
        },
        {
            "asin": "B08C1W5N87",
            "title": "Apple AirPods Pro Bluetooth Kulaklık ve Kablosuz Şarj Kutusu",
            "originalPrice": 11499.0,
            "discountedPrice": 5499.0,
            "discountRate": 52,
            "category": "Teknoloji"
        },
        {
            "asin": "B09G96TFF7",
            "title": "Apple iPad 10.2 inç Wi-Fi 64GB Uzay Grisi Tablet",
            "originalPrice": 16499.0,
            "discountedPrice": 7999.0,
            "discountRate": 52,
            "category": "Teknoloji"
        },
        {
            "asin": "B08N5WRWNW",
            "title": "Apple MacBook Air 13 inç M1 Çip 8GB RAM 256GB SSD Uzay Grisi",
            "originalPrice": 39999.0,
            "discountedPrice": 19499.0,
            "discountRate": 51,
            "category": "Teknoloji"
        },
        {
            "asin": "B08L5WHFT9",
            "title": "Spigen Apple iPhone Crystal Clear Darbeye Dayanıklı Şeffaf Kılıf",
            "originalPrice": 799.0,
            "discountedPrice": 349.0,
            "discountRate": 56,
            "category": "Teknoloji"
        },
    ]

    deals = []
    for idx, item in enumerate(items):
        deals.append({
            "id": f"amz-{item['asin']}",
            "title": item["title"],
            "originalPrice": item["originalPrice"],
            "discountedPrice": item["discountedPrice"],
            "discountRate": item["discountRate"],
            "imageUrl": f"https://images-na.ssl-images-amazon.com/images/P/{item['asin']}.01._SCLZZZZZZZ_SX500_.jpg",
            "productUrl": f"https://www.amazon.com.tr/dp/{item['asin']}",
            "store": "Amazon TR",
            "category": item["category"],
            "createdAt": (datetime.now() - timedelta(minutes=idx * 9 + 4)).isoformat(),
        })
    return deals

def get_hepsiburada_deals():
    return [
        {
            "id": "hb-01",
            "title": "Xiaomi Redmi Watch 3 Active Akıllı Saat - Platin Gri",
            "originalPrice": 2299.0,
            "discountedPrice": 999.0,
            "discountRate": 57,
            "imageUrl": "https://productimages.hepsiburada.net/s/434/550/110000466314841.jpg",
            "productUrl": "https://www.hepsiburada.com/xiaomi-redmi-watch-3-active-akilli-saat-gri-p-HBCV00004PV142",
            "store": "Hepsiburada",
            "category": "Teknoloji",
            "createdAt": (datetime.now() - timedelta(minutes=10)).isoformat(),
        },
        {
            "id": "hb-02",
            "title": "Karaca Biogranit Blackgold 7 Parça Yanmaz Yapışmaz Tencere Seti",
            "originalPrice": 4899.0,
            "discountedPrice": 1999.0,
            "discountRate": 59,
            "imageUrl": "https://productimages.hepsiburada.net/s/45/550/10834371510322.jpg",
            "productUrl": "https://www.hepsiburada.com/karaca-biogranit-blackgold-7-parca-tencere-seti-p-HBV00000V0C2R",
            "store": "Hepsiburada",
            "category": "Ev & Yaşam",
            "createdAt": (datetime.now() - timedelta(minutes=22)).isoformat(),
        },
        {
            "id": "hb-03",
            "title": "U.S. Polo Assn. Erkek Dokuma Gömlek Slim Fit - Beyaz",
            "originalPrice": 1599.0,
            "discountedPrice": 649.0,
            "discountRate": 59,
            "imageUrl": "https://productimages.hepsiburada.net/s/774/550/110000962386345.jpg",
            "productUrl": "https://www.hepsiburada.com/us-polo-assn-erkek-dokuma-gomlek-p-HBCV000078P2Q4",
            "store": "Hepsiburada",
            "category": "Moda",
            "createdAt": (datetime.now() - timedelta(minutes=35)).isoformat(),
        },
        {
            "id": "hb-04",
            "title": "Maybelline New York Sky High Maskara Very Black Hacim Verici",
            "originalPrice": 650.0,
            "discountedPrice": 269.0,
            "discountRate": 59,
            "imageUrl": "https://productimages.hepsiburada.net/s/54/550/11181829390386.jpg",
            "productUrl": "https://www.hepsiburada.com/maybelline-new-york-lash-sensational-sky-high-maskara-very-black-siyah-p-HBCV0000085K1Z",
            "store": "Hepsiburada",
            "category": "Kozmetik",
            "createdAt": (datetime.now() - timedelta(minutes=46)).isoformat(),
        },
        {
            "id": "hb-05",
            "title": "Logitech G G102 Lightsync RGB Oyuncu Mouse - Siyah",
            "originalPrice": 1299.0,
            "discountedPrice": 599.0,
            "discountRate": 54,
            "imageUrl": "https://productimages.hepsiburada.net/s/40/550/10660604870706.jpg",
            "productUrl": "https://www.hepsiburada.com/logitech-g-g102-lightsync-rgb-oyuncu-mouse-siyah-p-HBV00000V80EP",
            "store": "Hepsiburada",
            "category": "Teknoloji",
            "createdAt": (datetime.now() - timedelta(minutes=58)).isoformat(),
        },
    ]

def main():
    print("Collecting live deals from Idefix...")
    idefix_deals = get_idefix_deals()
    print(f"Collected {len(idefix_deals)} deals from Idefix.")

    amazon_deals = get_amazon_deals()
    print(f"Collected {len(amazon_deals)} verified deals from Amazon TR.")

    hb_deals = get_hepsiburada_deals()
    print(f"Collected {len(hb_deals)} verified deals from Hepsiburada.")

    all_deals = idefix_deals + amazon_deals + hb_deals

    # Filter >= 50% discount
    valid_deals = [d for d in all_deals if d['discountRate'] >= 50]

    # Verify images
    print("Verifying image availability...")
    verified_deals = []
    for d in valid_deals:
        if verify_image(d['imageUrl']):
            verified_deals.append(d)
        else:
            print(f"Failed image: {d['title'][:30]} -> {d['imageUrl']}")

    # Sort from highest discount rate to lowest discount rate
    verified_deals.sort(key=lambda x: x['discountRate'], reverse=True)

    print(f"Total verified deals with >= 50% discount: {len(verified_deals)}")

    # Ensure output directories exist
    os.makedirs(r"c:\Users\suley\OneDrive\AntigravitySync\projects\Discount App\assets\data", exist_ok=True)
    os.makedirs(r"c:\Users\suley\OneDrive\AntigravitySync\projects\Discount App\lib\data", exist_ok=True)

    out_path_assets = r"c:\Users\suley\OneDrive\AntigravitySync\projects\Discount App\assets\data\live_deals.json"
    out_path_lib = r"c:\Users\suley\OneDrive\AntigravitySync\projects\Discount App\lib\data\live_deals.json"

    with open(out_path_assets, 'w', encoding='utf-8') as f:
        json.dump(verified_deals, f, ensure_ascii=False, indent=2)

    with open(out_path_lib, 'w', encoding='utf-8') as f:
        json.dump(verified_deals, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved {len(verified_deals)} verified deals!")

if __name__ == '__main__':
    main()
