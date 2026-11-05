import json
from collections import Counter
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

with open('scraper/final_equal_verified_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print("=== TEST 1: VERİ BÜTÜNLÜĞÜ VE KATI TEKRARSIZLIK TESTİ ===")
print(f"Toplam Ürün: {len(catalog)}")
assert len(catalog) == 120, f"Hata: Toplam 120 olmalı, {len(catalog)} bulundu!"

stores = Counter(x['store'] for x in catalog)
print("Mağaza Dağılımı:", dict(stores))
assert stores['Amazon TR'] == 40, "Amazon TR tam 40 olmalı!"
assert stores['Hepsiburada'] == 40, "Hepsiburada tam 40 olmalı!"
assert stores['Idefix'] == 40, "Idefix tam 40 olmalı!"

cats = Counter(x['category'] for x in catalog)
print("Kategori Dağılımı:", dict(cats))
assert 28 <= cats['Teknoloji'] <= 32, "Teknoloji dengeli dağılmalı (~30)!"
assert 28 <= cats['Moda'] <= 32, "Moda dengeli dağılmalı (~30)!"
assert 28 <= cats['Ev & Yaşam'] <= 32, "Ev & Yaşam dengeli dağılmalı (~30)!"
assert 28 <= cats['Kozmetik'] <= 32, "Kozmetik dengeli dağılmalı (~30)!"
assert sum(cats.values()) == 120, "Toplam kategori toplamı 120 olmalı!"

# Fiyat ve indirim kontrolleri
for idx, x in enumerate(catalog):
    assert x['originalPrice'] > x['discountedPrice'], f"Hatalı fiyat #{idx}: {x['title']}"
    assert 15 <= x['discountRate'] <= 85, f"Hatalı indirim oranı #{idx}: {x['discountRate']}"
    assert x['productUrl'].startswith('http'), f"Geçersiz ürün linki #{idx}: {x['productUrl']}"
    assert x['imageUrl'].startswith('http'), f"Geçersiz resim linki #{idx}: {x['imageUrl']}"

# Marka-Tip Tekrarsızlık Kontrolü
seen_bt = Counter(x['brand_type'] for x in catalog)
duplicates = [k for k, v in seen_bt.items() if v > 1]
print(f"Mükerrer Marka & Tip Çifti Sayısı: {len(duplicates)}")
assert len(duplicates) == 0, f"Hata: Mükerrer marka-tip tespit edildi: {duplicates}"

# Kullanıcının belirttiği özel örnekler:
stanley_termos = [x for x in catalog if 'stanley' in x['title'].lower() and 'termos' in x['title'].lower()]
print(f"Stanley Termos Sayısı: {len(stanley_termos)} (Kural: En fazla 1)")
assert len(stanley_termos) <= 1, "Kural ihlali: 2 Stanley termos bulundu!"

xiaomi_kulaklik = [x for x in catalog if ('xiaomi' in x['title'].lower() or 'redmi' in x['title'].lower()) and ('kulakl' in x['title'].lower() or 'buds' in x['title'].lower())]
print(f"Xiaomi/Redmi Kulaklık Sayısı: {len(xiaomi_kulaklik)} (Kural: En fazla 1)")
assert len(xiaomi_kulaklik) <= 1, "Kural ihlali: 2 Xiaomi kulaklık bulundu!"

shirts = [x for x in catalog if x['ptype'] == 'gomlek']
print(f"Gömlek Sayısı: {len(shirts)} | Markalar: {[x['brand'] for x in shirts]}")
assert len(set(x['brand'] for x in shirts)) == len(shirts), "Kural ihlali: Aynı markadan birden fazla gömlek bulundu!"

# Çarpışma kontrolleri
store_col = sum(1 for i in range(len(catalog)-1) if catalog[i]['store'] == catalog[i+1]['store'])
cat_col = sum(1 for i in range(len(catalog)-1) if catalog[i]['category'] == catalog[i+1]['category'])
print(f"Ardışık Mağaza Çarpışması: {store_col} (Beklenen: 0)")
print(f"Ardışık Kategori Çarpışması: {cat_col} (Beklenen: 0)")
assert store_col == 0, "Ardışık mağaza çarpışması olmamalı!"
assert cat_col == 0, "Ardışık kategori çarpışması olmamalı!"

print("✅ TEST 1 BAŞARIYLA GEÇTİ!")
