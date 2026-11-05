import requests
import re
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings()

headers = {'User-Agent': 'Hepsiburada/5.32.0 (Android 13; SM-S908B)'}

queries = [
    'parfüm', 'erkek parfüm', 'kadın parfüm', 'deodorant', 'şampuan',
    'saç kremi', 'yüz serumu', 'nemlendirici', 'ruj', 'maskara',
    'göz kremi', 'vücut spreyi', 'kolonya', 'tıraş bıçağı', 'duş jeli'
]

found_deals = []
seen_urls = set()

for q in queries:
    search_url = f"https://www.hepsiburada.com/ara?q={requests.utils.quote(q)}"
    try:
        r = requests.get(search_url, headers=headers, verify=False, timeout=6)
        if r.status_code == 200:
            urls = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', r.text)
            for u in list(dict.fromkeys(urls))[:15]:
                full_url = 'https://www.hepsiburada.com' + u.split('?')[0]
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                
                # Check PDP
                pr = requests.get(full_url, headers=headers, verify=False, timeout=6)
                if pr.status_code == 200 and len(pr.text) > 15000:
                    soup = BeautifulSoup(pr.text, 'html.parser')
                    h1 = soup.find('h1')
                    title = h1.get_text().strip() if h1 else ''
                    if not title or len(title) < 5 or 'Güvenlik' in title:
                        continue
                    
                    # Extract prices
                    p_boxes = soup.select('span[data-test-id="variant-box-price"], [data-test-id="default-price"], del, [class*="Price"], [class*="price"]')
                    prices = []
                    for pb in p_boxes:
                        txt = pb.get_text().strip()
                        matches = re.findall(r'((?:\d{1,3}\.)*\d+,\d{2})', txt)
                        for m in matches:
                            try:
                                prices.append(float(m.replace('.', '').replace(',', '.')))
                            except:
                                pass
                    prices = sorted(list(set(prices)))
                    if len(prices) >= 2:
                        p_sale = prices[0]
                        p_orig = None
                        for p in prices[1:]:
                            if 1.15 <= (p / p_sale) <= 3.5:
                                p_orig = p
                                break
                        if p_orig:
                            rate = round(((p_orig - p_sale) / p_orig) * 100)
                            print(f"FOUND: [{q}] %{rate} | {p_sale} TL (was {p_orig} TL) | {title[:40]}")
                            found_deals.append({
                                'title': title,
                                'originalPrice': p_orig,
                                'discountedPrice': p_sale,
                                'discountRate': rate,
                                'productUrl': full_url
                            })
                            if len(found_deals) >= 12:
                                break
        if len(found_deals) >= 12:
            break
    except Exception as e:
        print(f"Error {q}: {e}")

print("Total found:", len(found_deals))
