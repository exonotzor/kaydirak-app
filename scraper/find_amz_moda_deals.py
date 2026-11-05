from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import sys
import json
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

moda_queries = [
    'erkek mont', 'kadin mont', 'erkek sweatshirt', 'kadin ceket',
    'erkek kazak', 'kadin hirka', 'spor ayakkabi', 'sirt cantasi'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9'
}

found_moda = []
seen_asins = set()

for q in moda_queries:
    if len(found_moda) >= 12:
        break
    url = f"https://www.amazon.com.tr/s?k={requests.utils.quote(q)}"
    try:
        r = requests.get(url, impersonate='chrome120', timeout=10, verify=False, headers=headers)
        asins = re.findall(r'data-asin="([B0-9A-Z]{10})"', r.text)
        print(f"[{q}] Found {len(asins)} ASINs")
        for asin in asins:
            if not asin or asin in seen_asins:
                continue
            seen_asins.add(asin)
            
            p_url = f"https://www.amazon.com.tr/dp/{asin}"
            try:
                pr = requests.get(p_url, impersonate='chrome120', timeout=8, verify=False, headers=headers)
                if pr.status_code != 200:
                    continue
                if 'Sayfa Bulunamadı' in pr.text or 'dogs of amazon' in pr.text.lower() or 'Şu anda mevcut değil' in pr.text:
                    continue
                m_title = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', pr.text, re.DOTALL)
                if not m_title:
                    continue
                title = m_title.group(1).strip()
                if len(title) < 5:
                    continue
                    
                # Extract image
                m_img = re.search(r'https://m\.media-amazon\.com/images/I/[^"\']+\.jpg', pr.text)
                img_url = m_img.group(0) if m_img else ''
                if not img_url:
                    continue
                    
                # Look for price
                # Try finding all prices on the page
                prices = []
                for p_match in re.finditer(r'((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', pr.text):
                    val_str = p_match.group(1).replace('.', '').replace(',', '.')
                    try:
                        v = float(val_str)
                        if 50 <= v <= 25000:
                            prices.append(v)
                    except Exception:
                        pass
                        
                prices = sorted(list(set(prices)))
                if len(prices) >= 2:
                    sale_p = prices[0]
                    orig_p = None
                    for p in prices[1:]:
                        ratio = p / sale_p
                        if 1.15 <= ratio <= 3.5:
                            orig_p = p
                            break
                    if orig_p:
                        rate = round(((orig_p - sale_p) / orig_p) * 100)
                        if 15 <= rate <= 75:
                            item = {
                                'id': f"amz-{asin}",
                                'asin': asin,
                                'title': title,
                                'originalPrice': orig_p,
                                'discountedPrice': sale_p,
                                'discountRate': rate,
                                'imageUrl': img_url,
                                'productUrl': p_url,
                                'store': 'Amazon TR',
                                'category': 'Moda'
                            }
                            found_moda.append(item)
                            print(f"  FOUND MODA [{len(found_moda)}]: %{rate} | {orig_p:.2f} -> {sale_p:.2f} | {title[:35]}")
                            if len(found_moda) >= 12:
                                break
            except Exception as e:
                pass
            time.sleep(0.15)
    except Exception as e:
        print(f"Error on {q}: {e}")

print(f"\nTotal live Moda deals harvested: {len(found_moda)}")
with open('scraper/harvested_live_amz_moda.json', 'w', encoding='utf-8') as f:
    json.dump(found_moda, f, ensure_ascii=False, indent=2)
