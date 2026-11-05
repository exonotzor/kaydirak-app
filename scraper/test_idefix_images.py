import requests
import urllib3
import json

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

with open('scraper/harvested_deals_raw.json', 'r', encoding='utf-8') as f:
    idefix_deals = json.load(f)

print(f"Loaded {len(idefix_deals)} Idefix deals.")
valid = 0
for d in idefix_deals[:10]:
    r = requests.head(d['imageUrl'], headers=headers, verify=False, timeout=5)
    print(f"Status: {r.status_code} | {d['title'][:40]} | {d['imageUrl'][:60]}")
    if r.status_code == 200:
        valid += 1
print(f"Valid images in sample: {valid}/10")
