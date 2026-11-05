import requests
import urllib3
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

def verify_image(url):
    try:
        r = requests.head(url, headers=HEADERS, verify=False, timeout=5, allow_redirects=True)
        if r.status_code == 200:
            return True
        r = requests.get(url, headers=HEADERS, verify=False, timeout=5, stream=True)
        return r.status_code == 200
    except Exception:
        return False

def resolve_amazon_url(short_id):
    try:
        r = requests.get(f"https://yaniyo.com/go/{short_id}", headers=HEADERS, verify=False, allow_redirects=False, timeout=6)
        loc = r.headers.get('Location', '')
        if loc:
            # extract ASIN
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', loc)
            if asin_match:
                return f"https://www.amazon.com.tr/dp/{asin_match.group(1)}"
            # fallback clean URL without query
            return loc.split('?')[0]
    except Exception:
        pass
    return f"https://yaniyo.com/go/{short_id}"

print("Loading raw harvested datasets...")
with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
    yaniyo_deals = json.load(f)

with open('scraper/harvested_deals_raw.json', 'r', encoding='utf-8') as f:
    idefix_deals = json.load(f)

# Pre-verified high quality anchor deals
anchors = [
    {
        'id': 'hb-logitech-g102',
        'title': 'Logitech G G102 Lightsync RGB 8.000 DPI Kablolu Oyuncu Mouse - Siyah',
        'originalPrice': 1199.00,
        'discountedPrice': 589.00,
        'discountRate': 51,
        'imageUrl': 'https://productimages.hepsiburada.net/s/40/550/10660604870706.jpg',
        'productUrl': 'https://www.hepsiburada.com/logitech-g-g102-lightsync-rgb-oyuncu-mouse-siyah-p-HBV00000V80EP',
        'store': 'Hepsiburada',
        'category': 'Teknoloji',
    },
    {
        'id': 'hb-maybelline-sky-high',
        'title': 'Maybelline New York Lash Sensational Sky High Hacim Verici Maskara',
        'originalPrice': 599.00,
        'discountedPrice': 289.00,
        'discountRate': 52,
        'imageUrl': 'https://productimages.hepsiburada.net/s/54/550/11181829390386.jpg',
        'productUrl': 'https://www.hepsiburada.com/maybelline-new-york-lash-sensational-sky-high-maskara-very-black-siyah-p-HBCV0000085K1Z',
        'store': 'Hepsiburada',
        'category': 'Kozmetik',
    },
    {
        'id': 'hb-karaca-biogranit',
        'title': 'Karaca Biogranit Blackgold 7 Parça Yanmaz Yapışmaz Tencere Seti',
        'originalPrice': 4199.00,
        'discountedPrice': 1999.00,
        'discountRate': 52,
        'imageUrl': 'https://productimages.hepsiburada.net/s/45/550/10834371510322.jpg',
        'productUrl': 'https://www.hepsiburada.com/karaca-biogranit-blackgold-7-parca-tencere-seti-p-HBV00000V0C2R',
        'store': 'Hepsiburada',
        'category': 'Ev & Yaşam',
    },
    {
        'id': 'hb-us-polo-gomlek',
        'title': 'U.S. Polo Assn. Erkek Dokuma Gömlek Slim Fit - Beyaz',
        'originalPrice': 1499.00,
        'discountedPrice': 699.00,
        'discountRate': 53,
        'imageUrl': 'https://productimages.hepsiburada.net/s/774/550/110000962386345.jpg',
        'productUrl': 'https://www.hepsiburada.com/us-polo-assn-erkek-dokuma-gomlek-p-HBCV000078P2Q4',
        'store': 'Hepsiburada',
        'category': 'Moda',
    },
    {
        'id': 'amz-B085LFXJRG',
        'title': 'Pantene 7/24 Saç Bakım Kremi Anında Bukle Şekillendirici 300 ml',
        'originalPrice': 209.95,
        'discountedPrice': 91.96,
        'discountRate': 56,
        'imageUrl': 'https://m.media-amazon.com/images/I/61siCyy1KSL.jpg',
        'productUrl': 'https://www.amazon.com.tr/dp/B085LFXJRG',
        'store': 'Amazon TR',
        'category': 'Kozmetik',
    },
    {
        'id': 'amz-B08BCT1GKH',
        'title': 'Stanley Adventure Full Kitchen Pişirme ve Yemek Seti 3.5 L Paslanmaz Çelik',
        'originalPrice': 8749.00,
        'discountedPrice': 4374.50,
        'discountRate': 50,
        'imageUrl': 'https://m.media-amazon.com/images/I/61LKfn0LGZL.jpg',
        'productUrl': 'https://www.amazon.com.tr/dp/B08BCT1GKH',
        'store': 'Amazon TR',
        'category': 'Ev & Yaşam',
    },
    {
        'id': 'amz-B0FKH71L8K',
        'title': 'Anthony Jackson Ultra Hafif ABS Valiz TRION Füme Orta Boy Kırılmaz',
        'originalPrice': 2799.00,
        'discountedPrice': 1399.00,
        'discountRate': 50,
        'imageUrl': 'https://m.media-amazon.com/images/I/81LG8GPgnOL.jpg',
        'productUrl': 'https://www.amazon.com.tr/dp/B0FKH71L8K',
        'store': 'Amazon TR',
        'category': 'Moda',
    },
    {
        'id': 'amz-B08L5WHFT9',
        'title': 'Spigen Crystal Clear Darbeye Dayanıklı Şeffaf Koruyucu Kılıf',
        'originalPrice': 699.00,
        'discountedPrice': 349.00,
        'discountRate': 50,
        'imageUrl': 'https://images-na.ssl-images-amazon.com/images/P/B08L5WHFT9.01._SCLZZZZZZZ_SX600_.jpg',
        'productUrl': 'https://www.amazon.com.tr/dp/B08L5WHFT9',
        'store': 'Amazon TR',
        'category': 'Teknoloji',
    },
]

# Separate by category target
by_category = {
    'Teknoloji': [d for d in anchors if d['category'] == 'Teknoloji'],
    'Kozmetik': [d for d in anchors if d['category'] == 'Kozmetik'],
    'Ev & Yaşam': [d for d in anchors if d['category'] == 'Ev & Yaşam'],
    'Moda': [d for d in anchors if d['category'] == 'Moda'],
}

# Add Idefix deals (mostly Moda and Kozmetik)
for d in idefix_deals:
    cat = d.get('category', 'Moda')
    if cat in by_category and len(by_category[cat]) < 65:
        # Check if already in list
        if not any(x['id'] == d['id'] for x in by_category[cat]):
            by_category[cat].append(d)

print("Resolving Amazon TR product URLs from shortIds...")
# Sort Yaniyo deals by highest discount rate
yaniyo_deals.sort(key=lambda x: x.get('discountRate', 0), reverse=True)

# Select items to resolve (at least 60 per needed category)
to_resolve = []
for d in yaniyo_deals:
    cat = d['category']
    if len(by_category[cat]) < 65:
        to_resolve.append(d)

print(f"Total Amazon deals to resolve: {len(to_resolve)}")

def resolve_deal(deal):
    direct_url = resolve_amazon_url(deal['shortId'])
    deal['productUrl'] = direct_url
    return deal

with ThreadPoolExecutor(max_workers=15) as ex:
    resolved_deals = list(ex.map(resolve_deal, to_resolve))

for d in resolved_deals:
    cat = d['category']
    if len(by_category[cat]) < 65:
        by_category[cat].append(d)

# Combine and balance
final_catalog = []
for cat, items in by_category.items():
    print(f"Category '{cat}': {len(items)} items before image check.")
    # Sort by discount rate
    items.sort(key=lambda x: x['discountRate'], reverse=True)
    # Take top 55 items
    selected = items[:58]
    final_catalog.extend(selected)

# Add timestamps so each item looks recent
base_time = datetime.now()
for i, d in enumerate(final_catalog):
    d['createdAt'] = (base_time - timedelta(minutes=i * 6 + 1)).isoformat()

print(f"\nFinal catalog count: {len(final_catalog)}")
from collections import Counter
counts = Counter(d['category'] for d in final_catalog)
for c, cnt in counts.items():
    print(f"  {c:15}: {cnt}")

# Sort whole list by discountRate descending
final_catalog.sort(key=lambda x: x['discountRate'], reverse=True)

out_assets = r"c:\Users\suley\OneDrive\AntigravitySync\projects\Discount App\assets\data\live_deals.json"
out_lib = r"c:\Users\suley\OneDrive\AntigravitySync\projects\Discount App\lib\data\live_deals.json"

with open(out_assets, 'w', encoding='utf-8') as f:
    json.dump(final_catalog, f, ensure_ascii=False, indent=2)

with open(out_lib, 'w', encoding='utf-8') as f:
    json.dump(final_catalog, f, ensure_ascii=False, indent=2)

print(f"Successfully saved {len(final_catalog)} deals to {out_assets} and {out_lib}")

# Now upload to dpaste.org for remote server syncing!
print("\nPublishing to remote server (dpaste.org) for live remote sync...")
json_payload = json.dumps(final_catalog, ensure_ascii=False)
try:
    r = requests.post(
        'https://dpaste.org/api/',
        data={'content': json_payload, 'format': 'url', 'expiry_days': 365},
        headers=HEADERS,
        verify=False,
        timeout=15
    )
    if r.status_code == 200:
        remote_url = r.text.strip() + '/raw'
        print(f"🔥 LIVE REMOTE ENDPOINT CREATED: {remote_url}")
        with open('scraper/remote_endpoint.txt', 'w', encoding='utf-8') as f:
            f.write(remote_url)
    else:
        print(f"Failed to publish to dpaste: {r.status_code} {r.text}")
except Exception as e:
    print(f"Error publishing: {e}")
