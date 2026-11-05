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

# 1. Collect candidate ASINs from multiple sources
candidate_asins = []

# From amz_deals_script.js
try:
    with open('scraper/amz_deals_script.js', 'r', encoding='utf-8') as f:
        candidate_asins.extend(re.findall(r'B0[A-Z0-9]{8}', f.read()))
except Exception:
    pass

# From amz_deals.html
try:
    with open('scraper/amz_deals.html', 'r', encoding='utf-8') as f:
        candidate_asins.extend(re.findall(r'B0[A-Z0-9]{8}', f.read()))
except Exception:
    pass

# From yaniyo_amazon_deals.json (resolve ASINs if needed)
try:
    with open('scraper/yaniyo_amazon_deals.json', 'r', encoding='utf-8') as f:
        y_deals = json.load(f)
        for yd in y_deals:
            img = yd.get('imageUrl', '')
            # often image contains ASIN or we have shortId
            m = re.search(r'/images/I/([A-Za-z0-9\-_]+)', img)
            sid = yd.get('shortId')
            # we also know some ASINs
except Exception:
    pass

# Deduplicate ASINs
candidate_asins = list(dict.fromkeys(candidate_asins))
print(f"Total candidate ASINs to inspect: {len(candidate_asins)}")

def check_asin(asin):
    url = f"https://www.amazon.com.tr/gp/aw/d/{asin}"
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=6)
        if r.status_code != 200 or len(r.text) < 15000:
            return None
            
        soup = BeautifulSoup(r.text, 'html.parser')
        t = soup.select_one('#title, #productTitle, h1')
        title = t.get_text().strip() if t else ''
        if not title or 'Robot Check' in title or 'Amazon' in title and len(title) < 15:
            return None
            
        # Clean title
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Check strike price
        strikes = re.findall(r'data-a-strike="true"[^>]*>.*?((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', r.text, re.DOTALL)
        if not strikes:
            strikes = re.findall(r'basisPrice.*?((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', r.text, re.DOTALL)
        if not strikes:
            strikes = re.findall(r'class="[^"]*a-text-price[^"]*"[^>]*>.*?((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', r.text, re.DOTALL)
            
        # Check sales price
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
        t_low = title.lower()
        cat = 'Teknoloji'
        if any(k in t_low for k in ['ayakkabı', 'ayakkabi', 'mont', 'ceket', 'gömlek', 'gomlek', 'pantolon', 'tişört', 'elbise', 'çanta', 'canta', 'polar', 'yelek', 'bot', 'çizme', 'parfüm']):
            if 'parfüm' in t_low:
                cat = 'Kozmetik'
            else:
                cat = 'Moda'
        elif any(k in t_low for k in ['krem', 'serum', 'şampuan', 'sampuan', 'losyon', 'güneş', 'gunes', 'cilt', 'bakım', 'bakim', 'diş']):
            cat = 'Kozmetik'
        elif any(k in t_low for k in ['termos', 'tencere', 'tava', 'bıçak', 'bicak', 'yastık', 'yorgan', 'havlu', 'nevresim', 'fincan', 'bardak', 'süpürge', 'temizlik', 'deterjan', 'matara', 'kupa']):
            cat = 'Ev & Yaşam'
            
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

print("Checking ASINs with 10 threads...")
verified_amz = []
with ThreadPoolExecutor(max_workers=10) as ex:
    for res in ex.map(check_asin, candidate_asins):
        if res:
            verified_amz.append(res)
            print(f"[{res['category']}] %{res['discountRate']} | {res['discountedPrice']} TL (was {res['originalPrice']} TL) | {res['title'][:40]}")

print(f"\nTotal verified Amazon TR deals: {len(verified_amz)}")
with open('scraper/amazon_verified_deals.json', 'w', encoding='utf-8') as f:
    json.dump(verified_amz, f, ensure_ascii=False, indent=2)
