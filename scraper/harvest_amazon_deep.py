import requests
import urllib3
import re
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

# 1. Resolve ASINs from yaniyo_amazon_deals.json
print("Resolving ASINs from yaniyo candidates...", flush=True)
all_asins = []

try:
    with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
        y_deals = json.load(f)
        
    def resolve_one(yd):
        sid = yd.get('shortId')
        cat = yd.get('category')
        if not sid:
            return None
        try:
            r = requests.get(f"https://yaniyo.com/go/{sid}", headers=headers, allow_redirects=False, verify=False, timeout=4)
            loc = r.headers.get('Location', '')
            m = re.search(r'/dp/([A-Z0-9]{10})', loc)
            if m:
                return (m.group(1), cat, yd.get('title'))
        except Exception:
            pass
        return None

    with ThreadPoolExecutor(max_workers=20) as ex:
        res = [r for r in ex.map(resolve_one, y_deals) if r]
        all_asins.extend(res)
    print(f"Resolved {len(all_asins)} ASINs from Yaniyo.", flush=True)
except Exception as e:
    print(f"Error resolving: {e}")

# 2. Add ASINs from deals script
try:
    with open('scraper/amz_deals_script.js', 'r', encoding='utf-8') as f:
        script_asins = re.findall(r'B0[A-Z0-9]{8}', f.read())
        for a in set(script_asins):
            all_asins.append((a, None, None))
except Exception:
    pass

# Deduplicate ASINs
unique_asins = {}
for item in all_asins:
    asin, cat, t = item
    if asin not in unique_asins:
        unique_asins[asin] = (cat, t)

print(f"Total unique ASINs to inspect: {len(unique_asins)}", flush=True)

def verify_amazon_deal(item):
    asin, (hint_cat, hint_title) = item
    url = f"https://www.amazon.com.tr/gp/aw/d/{asin}"
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=6)
        if r.status_code != 200 or len(r.text) < 15000:
            return None
            
        soup = BeautifulSoup(r.text, 'html.parser')
        t = soup.select_one('#title, #productTitle, h1')
        title = t.get_text().strip() if t else (hint_title or '')
        if not title or 'Robot Check' in title or ('Amazon' in title and len(title) < 15):
            return None
            
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Check strike price
        # Formats: 1.499,00 TL, 199,00 TL
        strikes = re.findall(r'data-a-strike="true"[^>]*>.*?((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', r.text, re.DOTALL)
        if not strikes:
            strikes = re.findall(r'basisPrice.*?((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', r.text, re.DOTALL)
        if not strikes:
            strikes = re.findall(r'class="[^"]*a-text-price[^"]*"[^>]*>.*?((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', r.text, re.DOTALL)
            
        sales = re.findall(r'priceToPay.*?((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', r.text, re.DOTALL)
        if not sales:
            sales = re.findall(r'apexPriceToPay.*?((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', r.text, re.DOTALL)
            
        if not strikes or not sales:
            return None
            
        s_val = float(strikes[0].replace('.', '').replace(',', '.'))
        p_val = float(sales[0].replace('.', '').replace(',', '.'))
        
        if s_val <= p_val or p_val <= 0 or s_val <= 0:
            return None
            
        rate = round(((s_val - p_val) / s_val) * 100)
        if rate < 10 or rate > 85:
            return None
            
        # Find high-res image
        img_el = soup.select_one('#landingImage, #main-image, img.a-dynamic-image')
        img_url = img_el.get('src') if img_el else ''
        if not img_url:
            imgs = re.findall(r'https://m\.media-amazon\.com/images/I/[A-Za-z0-9\-_%]+\.jpg', r.text)
            if imgs:
                img_url = imgs[0]
                
        if not img_url:
            return None
            
        # Determine category
        cat = hint_cat
        if not cat:
            t_low = title.lower()
            if any(k in t_low for k in ['ayakkabı', 'ayakkabi', 'mont', 'ceket', 'gömlek', 'gomlek', 'pantolon', 'tişört', 'elbise', 'çanta', 'canta', 'polar', 'yelek', 'bot', 'çizme']):
                cat = 'Moda'
            elif any(k in t_low for k in ['krem', 'serum', 'şampuan', 'sampuan', 'losyon', 'güneş', 'gunes', 'cilt', 'bakım', 'bakim', 'parfüm', 'parfum']):
                cat = 'Kozmetik'
            elif any(k in t_low for k in ['termos', 'tencere', 'tava', 'bıçak', 'bicak', 'yastık', 'yorgan', 'havlu', 'nevresim', 'fincan', 'bardak', 'süpürge', 'temizlik', 'deterjan', 'matara', 'kupa', 'blender', 'ütü']):
                cat = 'Ev & Yaşam'
            else:
                cat = 'Teknoloji'
                
        return {
            'id': f"amz-{asin}",
            'asin': asin,
            'title': title,
            'category': cat,
            'store': 'Amazon TR',
            'originalPrice': s_val,
            'discountedPrice': p_val,
            'discountRate': rate,
            'productUrl': f"https://www.amazon.com.tr/dp/{asin}",
            'imageUrl': img_url,
        }
    except Exception:
        return None

print(f"Verifying {len(unique_asins)} Amazon ASINs with 15 threads...", flush=True)
verified_amz = []
with ThreadPoolExecutor(max_workers=15) as ex:
    for res in ex.map(verify_amazon_deal, unique_asins.items()):
        if res:
            verified_amz.append(res)
            print(f"[{res['category']}] %{res['discountRate']} | {res['discountedPrice']} TL (was {res['originalPrice']} TL) | {res['title'][:40]}", flush=True)

print(f"\nTotal verified Amazon TR deals: {len(verified_amz)}", flush=True)
from collections import Counter
print(Counter(x['category'] for x in verified_amz))

with open('scraper/amazon_verified_deals.json', 'w', encoding='utf-8') as f:
    json.dump(verified_amz, f, ensure_ascii=False, indent=2)
print("Saved to scraper/amazon_verified_deals.json", flush=True)
