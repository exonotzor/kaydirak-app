import json
import requests
import urllib3
from datetime import datetime, timedelta

urllib3.disable_warnings()

with open('scraper/final_verified_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# Assign sequential createdAt timestamps
now = datetime.now()
for idx, d in enumerate(catalog):
    d['createdAt'] = (now - timedelta(minutes=idx * 4 + 1)).isoformat()

# Save locally to assets/data/live_deals.json and lib/data/live_deals.json
with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

try:
    with open('lib/data/live_deals.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
except Exception:
    pass

print(f"Catalog saved locally ({len(catalog)} deals).")

# Upload to Catbox
print("Uploading verified catalog to Catbox...")
r = requests.post(
    'https://catbox.moe/user/api.php',
    data={'reqtype': 'fileupload'},
    files={'fileToUpload': ('live_deals_v2.json', json.dumps(catalog, ensure_ascii=False), 'application/json')},
    verify=False,
    timeout=25
)

if r.status_code == 200 and r.text.startswith('http'):
    remote_url = r.text.strip()
    print(f"SUCCESS! Published remote URL: {remote_url}")
    with open('scraper/remote_url.txt', 'w', encoding='utf-8') as f:
        f.write(remote_url)
        
    # Verify download
    r_check = requests.get(remote_url, verify=False, timeout=10)
    if r_check.status_code == 200:
        downloaded = r_check.json()
        print(f"Verified remote download: successfully fetched {len(downloaded)} deals from {remote_url}!")
else:
    print(f"Catbox upload failed: {r.status_code} - {r.text}")
