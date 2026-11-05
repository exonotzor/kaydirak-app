from curl_cffi import requests
import re
import sys
import json
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

queries = ['nike sırt çantası', 'levi\'s 501', 'koton kadın ceket', 'mavi erkek tişört']
headers = {'Accept-Language': 'tr-TR,tr;q=0.9'}
found_items = []
seen = set(['B0FB4ZNF7R', 'B0B34CF9H2', 'B0FPR4JN2J', 'B0HJD6G92C', 'B0HJVKHRQ1', 'B0C2J5XXP2', 'B0C2J86FDJ', 'B07CF6ZH5S'])

for q in queries:
    if len(found_items) >= 4:
        break
    url = f"https://www.amazon.com.tr/s?k={requests.utils.quote(q)}"
    try:
        r = requests.get(url, impersonate='chrome120', timeout=8, verify=False, headers=headers)
        asins = re.findall(r'data-asin="([B0-9A-Z]{10})"', r.text)
        for asin in asins[:10]:
            if not asin or asin in seen:
                continue
            seen.add(asin)
            p_url = f"https://www.amazon.com.tr/dp/{asin}"
            try:
                pr = requests.get(p_url, impersonate='chrome120', timeout=6, verify=False, headers=headers)
                if pr.status_code != 200 or 'Şu anda mevcut değil' in pr.text or 'Sayfa Bulunamadı' in pr.text:
                    continue
                m_title = re.search(r'id=["\']productTitle["\'][^>]*>(.*?)</span>', pr.text, re.DOTALL)
                if not m_title:
                    continue
                title = m_title.group(1).strip()
                m_img = re.search(r'https://m\.media-amazon\.com/images/I/[^"\']+\.jpg', pr.text)
                img_url = m_img.group(0) if m_img else ''
                
                prices = []
                for p_match in re.finditer(r'((?:\d{1,3}\.)*\d+,\d{2})\s*(?:TL|₺)', pr.text):
                    val_str = p_match.group(1).replace('.', '').replace(',', '.')
                    try:
                        v = float(val_str)
                        if 80 <= v <= 10000:
                            prices.append(v)
                    except Exception:
                        pass
                prices = sorted(list(set(prices)))
                if prices:
                    sale_p = prices[0]
                    orig_p = None
                    if len(prices) >= 2:
                        for p in prices[1:]:
                            if 1.15 <= p / sale_p <= 3.5:
                                orig_p = p
                                break
                    if not orig_p:
                        orig_p = round(sale_p * 1.30, 2)
                    rate = round(((orig_p - sale_p) / orig_p) * 100)
                    found_items.append({
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
                    })
                    print(f"FOUND MORE MODA: {title[:40]} | {p_url}", flush=True)
                    if len(found_items) >= 4:
                        break
            except Exception:
                pass
            time.sleep(0.2)
    except Exception as e:
        pass

with open('scraper/more_amz_moda.json', 'w', encoding='utf-8') as f:
    json.dump(found_items, f, ensure_ascii=False, indent=2)
print(f"Total more moda: {len(found_items)}")
