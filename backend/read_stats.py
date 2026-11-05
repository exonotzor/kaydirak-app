import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SHARD_URLS = [
    "https://extendsclass.com/api/json-storage/bin/afacbcb",
    "https://extendsclass.com/api/json-storage/bin/cfffbde",
    "https://extendsclass.com/api/json-storage/bin/acbcbee",
    "https://extendsclass.com/api/json-storage/bin/cfcddea",
    "https://extendsclass.com/api/json-storage/bin/beecefb",
    "https://extendsclass.com/api/json-storage/bin/feecbab",
    "https://extendsclass.com/api/json-storage/bin/aeacdea",
    "https://extendsclass.com/api/json-storage/bin/bbcfdfd",
    "https://extendsclass.com/api/json-storage/bin/ceffccb",
    "https://extendsclass.com/api/json-storage/bin/acbcade",
    "https://extendsclass.com/api/json-storage/bin/bcaedda",
    "https://extendsclass.com/api/json-storage/bin/ecfdadb",
    "https://extendsclass.com/api/json-storage/bin/dfdeecf",
    "https://extendsclass.com/api/json-storage/bin/cdfbeef",
    "https://extendsclass.com/api/json-storage/bin/bcedcad",
    "https://extendsclass.com/api/json-storage/bin/eeedefb",
]


def fetch_shard(url):
    req = urllib.request.Request(
        url,
        headers={'Cache-Control': 'no-cache', 'User-Agent': 'KaydirakStatsReader/2.2'},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get('users', {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


all_users = {}
with ThreadPoolExecutor(max_workers=16) as ex:
    for shard_users in ex.map(fetch_shard, SHARD_URLS):
        if isinstance(shard_users, dict):
            all_users.update(shard_users)

print("=" * 65)
print("  KAYDIRAK CANLI KULLANICI İSTATİSTİKLERİ (16 SHARD BİRLEŞİK)")
print("=" * 65)
print(f"Toplam Kayıtlı Kullanıcı: {len(all_users)}\n")

sorted_users = sorted(
    all_users.values(),
    key=lambda x: x.get('lastSeenAt', ''),
    reverse=True,
)

for u in sorted_users:
    print(f"👤 Kullanıcı: {u.get('userId')} | Cihaz: {u.get('deviceInfo')}")
    print(
        f"   Giriş Sayısı: {u.get('sessionCount')} | Süre: {u.get('totalTimeMinutes', 0)} dk ({u.get('totalTimeHours', 0)} saat)"
    )
    print(
        f"   Gezilen Ürün: {u.get('viewedProductsCount')} | Mağazaya Tıklama: {u.get('totalClicks')}"
    )
    print(f"   Kategori Dağılımı: {u.get('categoryViews')}")
    clicks = u.get('clickedProducts', [])
    if clicks:
        print(f"   Son Tıklanan Ürünler ({len(clicks)}):")
        for c in clicks[:5]:
            print(f"     - [{c.get('store')}] {c.get('title')} ({c.get('price')} TL)")
    print("-" * 65)
