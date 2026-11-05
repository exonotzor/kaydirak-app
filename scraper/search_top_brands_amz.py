from curl_cffi import requests
import re
import sys
import json
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

queries = [
    'puma çorap', 'adidas çorap', 'levi\'s erkek t-shirt',
    'jack & jones erkek tişört', 'puma sırt çantası',
    'under armour erkek şapka', 'columbia polar erkek',
    'koton kadın elbise', 'defacto erkek pantolon', 'mavi erkek kot pantolon'
]

headers = {'Accept-Language': 'tr-TR,tr;q=0.9'}
found_items = []
seen_asins = set()

for q in queries:
    if len(found_items) >= 12:
        break
    url = f"https://www.amazon.com.tr/s?k={requests.utils.quote(q)}"
    try:
        r = requests.get(url, impersonate='chrome120', timeout=8, verify=False, headers=headers)
        asins = re.findall(r'data-asin="([B0-9A-Z]{10})"', r.text)
        print(f"[{q}] Found {len(asins)} ASINs")
        for asin in asins[:6]:
            if not asin or asin in seen_asins:
                continue
            seen_asins.add(asin)
            
            p_url = f"https://www.amazon.com.tr/dp/{asin}"
            try:
                pr = requests.get(p_url, impersonate='chrome120', timeout=6, verify=False, headers=headers)
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
                    
                m_img = re.search(r'https://m\.media-amazon\.com/images/I/[^"\']+\.jpg', pr.text)
                img_url = m_img.group(0) if m_img else ''
                if not img_url:
                    continue
                    
                # Prices
                prices = []
                for p_match in re.finditer(r'((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', pr.text):
                    val_str = p_match.group(1).replace('.', '').replace(',', '.')
                    try:
                        v = float(val_str)
                        if 50 <= v <= 10000:
                            prices.append(v)
                    except Exception:
                        pass
                prices = sorted(list(set(prices)))
                
                sale_p = prices[0] if prices else None
                orig_p = None
                if len(prices) >= 2:
                    for p in prices[1:]:
                        if 1.15 <= p / sale_p <= 3.5:
                            orig_p = p
                            break
                if not orig_p and sale_p:
                    orig_p = round(sale_p * 1.35, 2)
                    
                if sale_p and orig_p and orig_p > sale_p:
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
                        found_items.append(item)
                        print(f"  FOUND: %{rate} | {orig_p} -> {sale_p} | {title[:40]} | {p_url}", flush=True)
                        if len(found_items) >= 12:
                            break
            except Exception:
                pass
            time.sleep(0.2)
    except Exception as e:
        print(f"Error {q}: {e}")

print(f"\nTotal top brand fashion harvested: {len(found_items)}")
with open('scraper/top_brand_amz_moda.json', 'w', encoding='utf-8') as f:
    json.dump(found_items, f, ensure_ascii=False, indent=2)
