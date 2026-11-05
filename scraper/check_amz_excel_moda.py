from curl_cffi import requests
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

asins = [
    ('B0CHFFDYBN', "Levi's Graphic Standard Sweatshirt"),
    ('B0CHFFDQDX', "Levi's Original Zip-Up Sweatshirt Erkek"),
    ('B0B6BSS6T8', "Jack & Jones JJIEDDIE JJUTILITY AA 282 Pantolon"),
    ('B0CHFM61YT', "Levi's Ribcage Straight Jeans Kadın Kot"),
    ('B0CHFB433H', "Levi's Graphic Pullover Hoodie Sweatshirt"),
    ('B09Y7MGT51', "JACK & JONES JJXX JXMARY BLAZER DRESS"),
    ('B0DCXQXX3Q', "Levi's Authentic Hoodie Sweatshirt Erkek"),
    ('B09MJ31MHJ', "Levi's Donovan Western Gömlek"),
    ('B08DP638FZ', "Levi's 511 Slim Jeans Erkek Kot"),
    ('B0CVHGS2FR', "Levi's High Waist Mom Jean Pantolon"),
    ('B09RW28J7R', "Skechers Summits Kadın Siyah Spor Ayakkabı"),
    ('B08X6QQDC5', "ONLY Onlpoptrash-suki Life Pantolon"),
    ('B08QN9L73X', "Levi's The Trucker Jacket Mont Erkek"),
    ('B0C4GT8NQF', "JACK & JONES ORIGINALS JORVESTERBRO"),
    ('B0DCG1RHWT', "Salomon SPEEDCROSS 6 GTX Yürüyüş Ayakkabısı"),
    ('B0BGRFW654', "W Hovr Turbulence 2 Kadın Koşu Ayakkabısı"),
    ('B0888DKSGF', "ONLY Kadın Onlpoptrash Life Pantolon"),
    ('B0BD332XNR', "Levi's Effie Puffer Ceket Mont Erkek"),
]

headers = {'Accept-Language': 'tr-TR,tr;q=0.9'}

live_moda = []
for asin, label in asins:
    url = f"https://www.amazon.com.tr/dp/{asin}"
    try:
        r = requests.get(url, impersonate='chrome120', timeout=6, verify=False, headers=headers)
        is_404 = ('Sayfa Bulunamadı' in r.text) or ('dogs of amazon' in r.text.lower()) or r.status_code != 200
        is_out = ('Şu anda mevcut değil' in r.text) or ('Temporarily out of stock' in r.text)
        
        status = '404' if is_404 else ('OUT' if is_out else 'OK')
        m_title = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', r.text, re.DOTALL)
        t = m_title.group(1).strip() if m_title else label
        
        print(f"{asin}: {status} | HTTP {r.status_code} | {t[:45]}")
        if status == 'OK':
            live_moda.append((asin, t, url))
    except Exception as e:
        print(f"{asin}: ERROR {e}")

print(f"\nTotal verified in-stock fashion items from Excel: {len(live_moda)}")
