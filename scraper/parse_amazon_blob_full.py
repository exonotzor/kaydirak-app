import re
import json

with open('scraper/amazon_deals_blob.js', 'r', encoding='utf-8') as f:
    content = f.read()

matches = list(re.finditer(r'"priceToPay"', content))
print('Total matches:', len(matches))

high_deals = []
for i, m in enumerate(matches):
    start = max(0, m.start() - 300)
    end = min(len(content), m.start() + 1500)
    chunk = content[start:end]
    asin = re.search(r'"asin"\s*:\s*"([A-Z0-9]{10})"', chunk)
    price = re.search(r'"priceToPay"\s*:\s*\{[^}]*"price"\s*:\s*"([^"]+)"', chunk)
    basis = re.search(r'"basisPrice"\s*:\s*\{[^}]*"price"\s*:\s*"([^"]+)"', chunk)
    title = re.search(r'"title"\s*:\s*"([^"]+)"', chunk)
    imgs = re.findall(r'https://[^\s",]+\.(?:jpg|png)', chunk)
    if price and basis and asin and title:
        try:
            p = float(price.group(1).replace(',', '.'))
            b = float(basis.group(1).replace(',', '.'))
            if b > p and b > 0:
                rate = round(((b - p) / b) * 100)
                if rate >= 50:
                    high_deals.append({
                        'asin': asin.group(1),
                        'title': title.group(1),
                        'orig': b,
                        'disc': p,
                        'rate': rate,
                        'img': imgs[0] if imgs else None
                    })
        except Exception:
            pass

print('Deals with >= 50% discount:', len(high_deals))
for d in high_deals[:15]:
    print(f"-%{d['rate']} | {d['disc']} TL (was {d['orig']} TL) | {d['title'][:40]} | {d['asin']}")
