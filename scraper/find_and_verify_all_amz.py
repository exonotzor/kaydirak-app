import glob
import re
import json
from curl_cffi import requests
from bs4 import BeautifulSoup
import time
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Collect all real ASINs
all_asins = set()
for f in glob.glob('scraper/*.json') + glob.glob('scraper/*.py') + glob.glob('*.xlsx') + glob.glob('*.csv'):
    try:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            txt = fp.read()
            found = re.findall(r'B0[0-9A-Z]{8}', txt)
            for a in found:
                all_asins.add(a)
    except Exception:
        pass

# Also load existing verified
already_verified = {}
try:
    with open('scraper/amazon_strictly_live_deals.json', 'r', encoding='utf-8') as f:
        v_list = json.load(f)
        for v in v_list:
            already_verified[v['asin']] = v
except Exception:
    pass

print(f"Total ASINs discovered: {len(all_asins)}, already verified live: {len(already_verified)}")

# Filter to unverified
candidates = [a for a in sorted(all_asins) if a not in already_verified]
print(f"Candidates to check: {len(candidates)}")

live_new = []
for i, asin in enumerate(candidates):
    url = f"https://www.amazon.com.tr/dp/{asin}"
    try:
        r = requests.get(url, impersonate='chrome120', timeout=6, verify=False)
        if r.status_code != 200:
            continue
            
        if 'Sayfa Bulunamadı' in r.text or 'dogs of amazon' in r.text.lower() or 'köpek' in r.text.lower():
            continue
            
        if 'Şu anda mevcut değil' in r.text or 'Temporarily out of stock' in r.text:
            continue
            
        m_title = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', r.text, re.DOTALL)
        if not m_title:
            continue
        title = m_title.group(1).strip()
        if len(title) < 5:
            continue
            
        # Extract image
        m_img = re.search(r'https://m\.media-amazon\.com/images/I/[^"\']+\.jpg', r.text)
        img_url = m_img.group(0) if m_img else ''
        
        # Categorize
        tl = title.lower()
        cat = 'Diğer'
        if any(w in tl for w in ['mont', 'ceket', 'kaban', 'yelek', 'şort', 'sort', 'pantolon', 't-shirt', 'tişört', 'kazak', 'hırka', 'sweatshirt', 'ayakkabı', 'bot', 'sneaker', 'çorap', 'gömlek', 'polar', 'tayt', 'polo', 'jogger', 'eşofman', 'esofman']):
            cat = 'Moda'
        elif any(w in tl for w in ['tava', 'tencere', 'termos', 'bardak', 'fincan', 'bıçak', 'bicak', 'pike', 'nevresim', 'havlu', 'güveç', 'guvec', 'çatal', 'kaşık', 'mutfak', 'düdüklü', 'duduklu', 'sahan', 'saklama kabı']):
            cat = 'Ev & Yaşam'
        elif any(w in tl for w in ['krem', 'serum', 'şampuan', 'sampuan', 'losyon', 'parfüm', 'parfum', 'güneş', 'gunes', 'ruj', 'maske', 'sabun', 'diş', 'bb krem', 'fondöten']):
            cat = 'Kozmetik'
        elif any(w in tl for w in ['kulaklık', 'kulaklik', 'mouse', 'klavye', 'saat', 'hoparlör', 'hoparlor', 'şarj', 'sarj', 'pil', 'kablo', 'ssd', 'powerbank', 'adaptör', 'webcam', 'bellek', 'usb']):
            cat = 'Teknoloji'
            
        item = {
            'id': f"amz-{asin}",
            'asin': asin,
            'title': title,
            'productUrl': url,
            'imageUrl': img_url,
            'category': cat,
            'store': 'Amazon TR',
            'html': r.text[:10000] # save snippet for price extraction
        }
        live_new.append(item)
        print(f"[{len(live_new)}] FOUND LIVE [{cat}]: {title[:45]} | {url}")
    except Exception:
        pass
    time.sleep(0.15)

print(f"\nDiscovered {len(live_new)} additional live in-stock Amazon products!")
with open('scraper/discovered_live_amazon.json', 'w', encoding='utf-8') as f:
    json.dump(live_new, f, ensure_ascii=False, indent=2)
