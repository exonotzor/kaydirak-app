import urllib.request
import json

req = urllib.request.Request(
    'https://api.github.com/gists',
    data=json.dumps({"description": "deals", "public": True, "files": {"deals.json": {"content": "[]"}}}).encode('utf-8'),
    headers={'User-Agent': 'AntigravityApp', 'Content-Type': 'application/json'},
    method='POST'
)
try:
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code, e.read().decode('utf-8'))
