import json
from collections import Counter
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

for fname in ['idefix_strict_onpage.json', 'idefix_all_categories.json']:
    with open(f'scraper/{fname}', 'r', encoding='utf-8') as f:
        d = json.load(f)
    print(f"{fname}: {len(d)} items, Categories: {dict(Counter(x.get('category') for x in d))}")
