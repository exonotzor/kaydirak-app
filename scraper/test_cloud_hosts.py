import urllib.request
import json

# 1. npoint.io
try:
    req = urllib.request.Request('https://api.npoint.io', data=json.dumps({"test": 123}).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=5) as r:
        print('npoint POST:', r.status, r.read().decode('utf-8'))
except Exception as e:
    print('npoint error:', e)

# 2. kvdb.io (create bucket)
try:
    req = urllib.request.Request('https://kvdb.io', data=b'', method='POST')
    with urllib.request.urlopen(req, timeout=5) as r:
        bucket = r.read().decode('utf-8').strip()
        print('kvdb bucket:', bucket)
        # Put key
        req_put = urllib.request.Request(f'https://kvdb.io/{bucket}/deals', data=b'[{"msg":"hello"}]', method='POST')
        with urllib.request.urlopen(req_put, timeout=5) as r2:
            print('kvdb put:', r2.status)
        # Get key
        with urllib.request.urlopen(f'https://kvdb.io/{bucket}/deals', timeout=5) as r3:
            print('kvdb get:', r3.status, r3.read().decode('utf-8'))
except Exception as e:
    print('kvdb error:', e)

# 3. jsonstorage.net
try:
    req = urllib.request.Request('https://api.jsonstorage.net/v1/json', data=json.dumps([{"test": 123}]).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=5) as r:
        print('jsonstorage POST:', r.status, r.read().decode('utf-8'))
except Exception as e:
    print('jsonstorage error:', e)
