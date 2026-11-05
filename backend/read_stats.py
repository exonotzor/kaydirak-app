import urllib.request
import json
import sys
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BIN_URL = f"https://extendsclass.com/api/json-storage/bin/afacbcb?t={int(time.time()*1000)}"
req = urllib.request.Request(BIN_URL, headers={'User-Agent': 'KaydirakAnalyticsReader/1.0'})
with urllib.request.urlopen(req, timeout=10) as r:
    data = json.loads(r.read().decode('utf-8'))

users = data.get('users', {})
print(f"=== KAYDIRAK CANLI KULLANICI İSTATİSTİKLERİ (Son Güncelleme: {data.get('updatedAt')}) ===")
print(f"Toplam Tekil Kullanıcı: {len(users)}\n")

for uid, u in users.items():
    print(f"👤 Kullanıcı: {uid} ({u.get('deviceInfo')})")
    print(f"   - Giriş Sayısı     : {u.get('sessionCount')} kez")
    print(f"   - Geçirilen Süre   : {u.get('totalTimeSeconds')} sn ({u.get('totalTimeMinutes')} dk / {u.get('totalTimeHours')} saat)")
    print(f"   - Gezilen Ürün     : {u.get('viewedProductsCount')} ürün | Dağılım: {u.get('categoryViews')}")
    print(f"   - Mağaza Tıklaması : {u.get('totalClicks')} tık")
    print(f"   - Son Aktif Zaman  : {u.get('lastSeenAt')}")
    clicks = u.get('clickedProducts', [])
    if clicks:
        print(f"   - Son Tıkladığı Ürünler:")
        for c in clicks[:5]:
            print(f"     * [{c.get('store')}] {c.get('title')} ({c.get('price')} TL) @ {c.get('clickedAt')}")
    print()
