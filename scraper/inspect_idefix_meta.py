import requests
import json
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

url = 'https://www.idefix.com/cep-telefonu-aksesuarlari-c-2313374140'
r = requests.get(url, headers=headers, verify=False, timeout=8)
soup = BeautifulSoup(r.text, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')
if script and script.string:
    data = json.loads(script.string)
    pp = data.get('props', {}).get('pageProps', {})
    cd = pp.get('categoryData', {})
    print("categoryData keys:", list(cd.keys()))
    sort_opts = cd.get('sortOptions') or cd.get('sortings') or cd.get('sort')
    print("Sort options:", sort_opts)
    filters = cd.get('filters') or cd.get('facets') or []
    print(f"Filters count: {len(filters)}")
    for f in filters[:5]:
        print(f"Filter: {f.get('title') or f.get('name')} | key: {f.get('key') or f.get('code')}")
