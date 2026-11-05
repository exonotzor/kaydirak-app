import requests
import urllib3

urllib3.disable_warnings()

url = "https://catbox.moe/user/api.php"
with open('scraper/final_equal_verified_catalog.json', 'rb') as f:
    files = {'fileToUpload': ('live_deals.json', f, 'application/json')}
    data = {'reqtype': 'fileupload'}
    r = requests.post(url, data=data, files=files, verify=False, timeout=15)
    print("Upload status:", r.status_code)
    print("Remote URL:", r.text.strip())
