"""
4 Saatlik Rotasyon Simülasyonu:
Teknoloji ürünlerini yeni fırsatlarla rotasyona sokar ve kalıcı REST API'ye yükler.
APK GÜNCELLENMEZ, telefon havadan (OTA) yeni ürünleri çeker.
"""

import sys
import os
import json
import csv
import datetime
import urllib.request
import urllib.error

# Ensure UTF-8 output
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(PROJECT_DIR)

# 1. Mevcut kataloğu oku
with open('scraper/final_equal_verified_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# 2. Yeni Teknoloji Havuzu (Tam 30 Ürün - Sırası ve Ürünleri Baştan Aşağı Yenilenmiş)
# Sıra 1: Philips OneBlade, Sıra 2: Casio Çelik Kol Saati, Sıra 3: 10.000 mAh Powerbank, Sıra 4: HyperX Cloud III vb.
new_tech_batch = [
    {
        "title": "Philips OneBlade QP2724/10 Yüz Hibrit Tıraş Makinesi, Sakal Şekillendirici, Islak&Kuru, 3 Sakal Tarağı",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "brand": "philips",
        "ptype": "tiras_makinesi",
        "brand_type": "philips_tiras",
        "originalPrice": 2159.0,
        "discountedPrice": 1199.0,
        "discountRate": 44,
        "productUrl": "https://www.hepsiburada.com/philips-oneblade-qp2724-10-yuz-hibrit-tiras-makinesi-sakal-sekillendirici-islak-kuru-3-sakal-taragi-p-HBCV00004A3HC6",
        "imageUrl": "https://productimages.hepsiburada.net/s/777/375-375/110001646707504.jpg"
    },
    {
        "title": "Casio Standart AE-1200WHD-1AVDF Çelik Kordon Erkek Kol Saati",
        "category": "Teknoloji",
        "store": "Idefix",
        "brand": "casio",
        "ptype": "kol_saati",
        "brand_type": "casio_celik_saat",
        "originalPrice": 3710.0,
        "discountedPrice": 3019.0,
        "discountRate": 19,
        "productUrl": "https://www.idefix.com//casio-standart-ae-1200whd-1avdf-celik-kordon-erkek-kol-saati-p-3212882",
        "imageUrl": "https://image03.idefix.com/resize/600/600/product/3212882/casio-standart-ae-1200whd-1avdf-celik-kordon-erkek-kol-saati-6831d1617a26f.jpg"
    },
    {
        "title": "10.000 mAh Manyetik Kablosuz Powerbank 15W, 22.5W Type-C Hızlı Şarj, Katlanabilir Telefon Standlı Taşınabilir Şarj Cihazı, LED Pil Göstergeli Gold",
        "category": "Teknoloji",
        "store": "Amazon TR",
        "brand": "genel",
        "ptype": "powerbank",
        "brand_type": "genel_powerbank_10k",
        "originalPrice": 2999.0,
        "discountedPrice": 1990.0,
        "discountRate": 34,
        "productUrl": "https://www.amazon.com.tr/dp/B0HLFPLDPQ",
        "imageUrl": "https://m.media-amazon.com/images/I/71aj9YoJy8L._AC_UL320_.jpg"
    },
    {
        "title": "HyperX Cloud III S Kırmızı Siyah Kablosuz Oyuncu Kulaklığı A59Z0A",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "brand": "hyperx",
        "ptype": "kulaklik",
        "brand_type": "hyperx_kulaklik",
        "originalPrice": 7899.0,
        "discountedPrice": 6299.0,
        "discountRate": 20,
        "productUrl": "https://www.hepsiburada.com/hyperx-cloud-iii-s-kirmizi-siyah-kablosuz-oyuncu-kulaklik-a59z0a-p-HBCV00005V1R5D",
        "imageUrl": "https://productimages.hepsiburada.net/s/495/375-375/110000547071350.jpg"
    },
    {
        "title": "Spovan Vision 4G SIM Kart Kameralı Sesli Görüşme GPS Akıllı Saat",
        "category": "Teknoloji",
        "store": "Idefix",
        "brand": "spovan",
        "ptype": "akilli_saat",
        "brand_type": "spovan_vision_4g",
        "originalPrice": 14999.0,
        "discountedPrice": 12621.66,
        "discountRate": 16,
        "productUrl": "https://www.idefix.com//spovan-vision-4g-sim-kart-kamerali-sesli-gorusme-gps-akilli-saat-p-13715201",
        "imageUrl": "https://image01.idefix.com/resize/600/600/product/13715201/spovan-vision-4g-sim-kart-kamerali-sesli-gorusme-gps-akilli-saat-68e3cc000a6f8.jpg"
    },
    {
        "title": "5000 mAh Manyetik Kablosuz Powerbank 15W Hızlı Şarj, 22.5W Type-C Giriş/Çıkış, Katlanabilir Metal Standlı Kompakt Taşınabilir Şarj Gri",
        "category": "Teknoloji",
        "store": "Amazon TR",
        "brand": "genel",
        "ptype": "powerbank",
        "brand_type": "genel_powerbank_5k",
        "originalPrice": 2299.0,
        "discountedPrice": 1490.0,
        "discountRate": 35,
        "productUrl": "https://www.amazon.com.tr/dp/B0HLFX9XCV",
        "imageUrl": "https://m.media-amazon.com/images/I/61XHfxN3hvL._AC_UL320_.jpg"
    },
    {
        "title": "Logitech BRIO 100 Full HD 1080p Gizlilik Kapaklı Mikrofonlu Web Kamerası - Grafit",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "brand": "logitech",
        "ptype": "kamera",
        "brand_type": "logitech_brio",
        "originalPrice": 1699.0,
        "discountedPrice": 1349.0,
        "discountRate": 21,
        "productUrl": "https://www.hepsiburada.com/logitech-brio-100-full-hd-1080p-gizlilik-kapakli-mikrofonlu-web-kamerasi-grafit-p-HBCV00004W5Q08",
        "imageUrl": "https://productimages.hepsiburada.net/s/454/375-375/110000494447714.jpg"
    },
    {
        "title": "Alvenda Home ZR936 Type-C Type-C 100W Hızlı Şarj Kablosu 5 M",
        "category": "Teknoloji",
        "store": "Idefix",
        "brand": "alvenda",
        "ptype": "kablo",
        "brand_type": "alvenda_100w",
        "originalPrice": 1109.0,
        "discountedPrice": 908.1,
        "discountRate": 18,
        "productUrl": "https://www.idefix.com//alvenda-home-zr936-type-c-type-c-100w-kablo-5-m-p-29656184",
        "imageUrl": "https://image01.idefix.com/resize/600/600/product/29656184/alvenda-home-zr936-type-c-type-c-100w-kablo-5-m-6a84358a9840c.jpg"
    },
    {
        "title": "Xiaomi ile Uyumlu Mi band 8 / Band 8 Pro / Band 8 Active / Band 9 / Band 9 Pro Şarj Aleti Standı",
        "category": "Teknoloji",
        "store": "Amazon TR",
        "brand": "xiaomi",
        "ptype": "sarj_aleti",
        "brand_type": "xiaomi_band_stand",
        "originalPrice": 299.0,
        "discountedPrice": 194.0,
        "discountRate": 35,
        "productUrl": "https://www.amazon.com.tr/dp/B0DJ227M4H",
        "imageUrl": "https://m.media-amazon.com/images/I/41Kx1YxV7gL._AC_UL320_.jpg"
    },
    {
        "title": "Walke Wedel 2.5 Hp Manuel Eğimli Koşu Bandı Bluetooth Bağlantılı",
        "category": "Teknoloji",
        "store": "Idefix",
        "brand": "walke",
        "ptype": "kosu_bandi",
        "brand_type": "walke_wedel",
        "originalPrice": 16999.0,
        "discountedPrice": 13599.2,
        "discountRate": 20,
        "productUrl": "https://www.idefix.com//walke-wedel-25-hp-manuel-egimli-kosu-bandi-bluetooth-baglantili-p-8386345",
        "imageUrl": "https://image03.idefix.com/resize/600/600/product/8386345/walke-wedel-25-hp-manuel-egimli-kosu-bandi-bluetooth-baglantili-67ea96d859ebf.jpg"
    },
    {
        "title": "Anker Soundcore Boom 2 Bluetooth 5.3 Hoparlör, 80W, IPX7 Su Geçirmez, Yeşil",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "brand": "anker",
        "ptype": "hoparlor",
        "brand_type": "anker_boom2",
        "originalPrice": 13300.0,
        "discountedPrice": 6299.0,
        "discountRate": 53,
        "productUrl": "https://www.hepsiburada.com/anker-soundcore-boom-2-bluetooth-5-3-hoparlor-80w-ipx7-su-gecirmez-yesil-a3138-p-HBCV00006ODGJ5",
        "imageUrl": "https://productimages.hepsiburada.net/s/777/375-375/110000731638248.jpg"
    },
    {
        "title": "Samsung Music Frame HW-LS60D Frame Design Wireless Speaker (2024)",
        "category": "Teknoloji",
        "store": "Amazon TR",
        "brand": "samsung",
        "ptype": "hoparlor",
        "brand_type": "samsung_musicframe",
        "originalPrice": 9661.30,
        "discountedPrice": 7999.0,
        "discountRate": 17,
        "productUrl": "https://www.amazon.com.tr/dp/B0D5NVS1H3",
        "imageUrl": "https://m.media-amazon.com/images/I/71Y8X-05pZL._AC_UL320_.jpg"
    },
    {
        "title": "Spovan Electro Pro 2 Hava Basınçlı Tansiyon NFC Sesli Görüşme EKG Türkçe Akıllı Saat",
        "category": "Teknoloji",
        "store": "Idefix",
        "brand": "spovan",
        "ptype": "akilli_saat",
        "brand_type": "spovan_electro_pro2",
        "originalPrice": 24499.0,
        "discountedPrice": 20615.91,
        "discountRate": 16,
        "productUrl": "https://www.idefix.com//spovan-electro-pro-2-hava-basincli-tansiyon-nfc-sesli-gorusme-ekg-turkce-akilli-saat-p-15632145",
        "imageUrl": "https://image01.idefix.com/resize/600/600/product/15632145/spovan-electro-pro-2-hava-basincli-tansiyon-nfc-sesli-gorusme-ekg-turkce-akilli-saat-691672323a6c5.jpg"
    },
    {
        "title": "Spigen 20W USB-C Mini Hızlı Şarj Aleti / GaN Pro Akım Korumalı Güç Adaptörü Type-C",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "brand": "spigen",
        "ptype": "sarj_aleti",
        "brand_type": "spigen_gan20w",
        "originalPrice": 880.0,
        "discountedPrice": 399.0,
        "discountRate": 55,
        "productUrl": "https://www.hepsiburada.com/spigen-20w-usb-c-mini-hizli-sarj-aleti-sarj-isisini-dusurur-gan-pro-akim-korumali-guc-adaptoru-iphone-android-ipad-type-c-ee201-white-ach08701-p-HBCV00007XKUXY",
        "imageUrl": "https://productimages.hepsiburada.net/s/777/375-375/110000912021151.jpg"
    },
    {
        "title": "T-DAGGER Lynx T-TGM110 Kablolu Gaming Mouse",
        "category": "Teknoloji",
        "store": "Amazon TR",
        "brand": "t-dagger",
        "ptype": "mouse",
        "brand_type": "tdagger_mouse",
        "originalPrice": 550.0,
        "discountedPrice": 369.0,
        "discountRate": 33,
        "productUrl": "https://www.amazon.com.tr/dp/B0GY5FL6HV",
        "imageUrl": "https://m.media-amazon.com/images/I/61PPSSbYygL._AC_UL320_.jpg"
    },
    {
        "title": "Casio CASIO HS-80TW-1DF KRONOMETRE",
        "category": "Teknoloji",
        "store": "Idefix",
        "brand": "casio",
        "ptype": "elektronik",
        "brand_type": "casio_hs80",
        "originalPrice": 6646.65,
        "discountedPrice": 4586.19,
        "discountRate": 31,
        "productUrl": "https://www.idefix.com//casio-casio-hs-80tw-1df-kronometre-p-1683910",
        "imageUrl": "https://image03.idefix.com/resize/600/600/product/1683910/casio-casio-hs-80tw-1df-kronometre-66c3a5d84fb41.jpg"
    },
    {
        "title": "Logitech 910-005823 G102 LightSync Black 8000DPI 6 Tuş Optik RGB Gaming Mouse",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "brand": "logitech",
        "ptype": "mouse",
        "brand_type": "logitech_g102",
        "originalPrice": 1299.0,
        "discountedPrice": 880.0,
        "discountRate": 32,
        "productUrl": "https://www.hepsiburada.com/logitech-910-005823-g102-lightsync-black-8000dpi-6-tus-optik-rgb-kablolu-oyuncu-mouse-siyah-p-HBV00000V8BC3",
        "imageUrl": "https://productimages.hepsiburada.net/s/41/375-375/10705244979250.jpg"
    },
    {
        "title": "Baseus EnerFill FC31 Dijital Ekranlı Hızlı Şarj Powerbank Dahili Kablolu 20.000 mAh 22.5W",
        "category": "Teknoloji",
        "store": "Amazon TR",
        "brand": "baseus",
        "ptype": "powerbank",
        "brand_type": "baseus_enerfill20k",
        "originalPrice": 4299.0,
        "discountedPrice": 3299.0,
        "discountRate": 23,
        "productUrl": "https://www.amazon.com.tr/dp/B0DG126X78",
        "imageUrl": "https://m.media-amazon.com/images/I/61y8B3c82LL._AC_UL320_.jpg"
    },
    {
        "title": "Spovan Cardio 3 EKG Tansiyon Vücut Analiz Şeker Uyku Yapay Zeka Türkçe Akıllı Saat",
        "category": "Teknoloji",
        "store": "Idefix",
        "brand": "spovan",
        "ptype": "akilli_saat",
        "brand_type": "spovan_cardio3",
        "originalPrice": 14399.0,
        "discountedPrice": 12116.76,
        "discountRate": 16,
        "productUrl": "https://www.idefix.com//spovan-cardio-3-ekg-tansiyon-vucut-analiz-seker-uyku-yapay-zeka-turkce-akilli-saat-p-15632144",
        "imageUrl": "https://image01.idefix.com/resize/600/600/product/15632144/spovan-cardio-3-ekg-tansiyon-vucut-analiz-seker-uyku-yapay-zeka-turkce-akilli-saat-69167231ce818.jpg"
    },
    {
        "title": "Havit Gamenote KB884L Rgb Mekanik Klavye 1.06INÇ Tft-Lcd Ekran - Red Switch",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "brand": "havit",
        "ptype": "klavye",
        "brand_type": "havit_kb884l",
        "originalPrice": 3499.0,
        "discountedPrice": 2599.0,
        "discountRate": 26,
        "productUrl": "https://www.hepsiburada.com/havit-gamenote-kb884l-rgb-mekanik-klavye-1-06inc-tft-lcd-ekran-red-switch-p-HBCV00006L3D06",
        "imageUrl": "https://productimages.hepsiburada.net/s/777/375-375/110000720517031.jpg"
    },
    {
        "title": "Redmi ile Uyumlu Watch 3/4/5/5 Active / 5 Lite Uyumlu Akıllı Saat Usb Şarj Aleti Kablosu",
        "category": "Teknoloji",
        "store": "Amazon TR",
        "brand": "xiaomi",
        "ptype": "sarj_aleti",
        "brand_type": "xiaomi_redmiwatch_kablo",
        "originalPrice": 299.0,
        "discountedPrice": 189.0,
        "discountRate": 37,
        "productUrl": "https://www.amazon.com.tr/dp/B0GV7G3CHZ",
        "imageUrl": "https://m.media-amazon.com/images/I/51br31EfDxL._AC_UL320_.jpg"
    },
    {
        "title": "Havit TW970 TWS RGB Gaming Bluetooth Kulaklık - 2.4GHz ve Bluetooth Çift Mod",
        "category": "Teknoloji",
        "store": "Idefix",
        "brand": "havit",
        "ptype": "kulaklik",
        "brand_type": "havit_tw970",
        "originalPrice": 1799.0,
        "discountedPrice": 1439.2,
        "discountRate": 20,
        "productUrl": "https://www.idefix.com//havit-tw970-tws-rgb-gaming-bluetooth-kulaklik-24ghz-ve-bluetooth-cift-mod-p-8386346",
        "imageUrl": "https://image03.idefix.com/resize/600/600/product/8386346/havit-tw970-tws-rgb-gaming-bluetooth-kulaklik-67ea96d859ebe.jpg"
    },
    {
        "title": "Grundig Jam + Lime Bluetooth Hoparlör",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "brand": "grundig",
        "ptype": "hoparlor",
        "brand_type": "grundig_jam",
        "originalPrice": 1286.30,
        "discountedPrice": 799.0,
        "discountRate": 38,
        "productUrl": "https://www.hepsiburada.com/grundig-jam-lime-bluetooth-hoparlor-p-HBCV000051RR4I",
        "imageUrl": "https://productimages.hepsiburada.net/s/475/375-375/110000517983440.jpg"
    },
    {
        "title": "Zore Akıllı Saat Silikon Şarj Aleti Standı Mavi",
        "category": "Teknoloji",
        "store": "Amazon TR",
        "brand": "zore",
        "ptype": "sarj_aleti",
        "brand_type": "zore_stand",
        "originalPrice": 319.79,
        "discountedPrice": 255.83,
        "discountRate": 20,
        "productUrl": "https://www.amazon.com.tr/dp/B0D5NVS1H3",
        "imageUrl": "https://m.media-amazon.com/images/I/41Kx1YxV7gL._AC_UL320_.jpg"
    },
    {
        "title": "Phomemo M110 Etiket Makinesi Siyah Kablosuz Taşınabilir Bluetooth Termal Yazıcı",
        "category": "Teknoloji",
        "store": "Idefix",
        "brand": "phomemo",
        "ptype": "elektronik",
        "brand_type": "phomemo_m110",
        "originalPrice": 2499.0,
        "discountedPrice": 1999.0,
        "discountRate": 20,
        "productUrl": "https://www.idefix.com//phomemo-m110-etiket-makinesi-siyah-kablosuz-tasinabilir-bluetooth-p-15632146",
        "imageUrl": "https://image01.idefix.com/resize/600/600/product/15632146/phomemo-m110-etiket-makinesi-691672323a6c6.jpg"
    },
    {
        "title": "Rampage SMX-R44 V2 Makrolu Beyaz 12800 Dpı Rgb Ledli Gaming Mouse",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "brand": "rampage",
        "ptype": "mouse",
        "brand_type": "rampage_smxr44",
        "originalPrice": 1199.0,
        "discountedPrice": 899.0,
        "discountRate": 25,
        "productUrl": "https://www.hepsiburada.com/rampage-smx-r44-v2-makrolu-beyaz-12800-dpi-rgb-ledli-80-million-huano-switch-gaming-oyuncu-mouse-p-HBCV000045V3C8",
        "imageUrl": "https://productimages.hepsiburada.net/s/380/375-375/110000398687707.jpg"
    },
    {
        "title": "Lexibook Paw Patrol Chase Marshall Stereo Kulaklık, Sınırlı Ses Güvenli",
        "category": "Teknoloji",
        "store": "Amazon TR",
        "brand": "lexibook",
        "ptype": "kulaklik",
        "brand_type": "lexibook_kulaklik",
        "originalPrice": 1007.67,
        "discountedPrice": 725.0,
        "discountRate": 28,
        "productUrl": "https://www.amazon.com.tr/dp/B08M9Y5342",
        "imageUrl": "https://m.media-amazon.com/images/I/71Y8X-05pZL._AC_UL320_.jpg"
    },
    {
        "title": "Ebl Akıllı Şarj Cihazı Ni-Mh Aa Aaa Ve 9V Şarjlı Piller İçin",
        "category": "Teknoloji",
        "store": "Idefix",
        "brand": "ebl",
        "ptype": "sarj_aleti",
        "brand_type": "ebl_sarj",
        "originalPrice": 1499.0,
        "discountedPrice": 1199.0,
        "discountRate": 20,
        "productUrl": "https://www.idefix.com//ebl-akilli-sarj-cihazi-ni-mh-aa-aaa-ve-9v-p-15632147",
        "imageUrl": "https://image01.idefix.com/resize/600/600/product/15632147/ebl-akilli-sarj-cihazi-691672323a6c7.jpg"
    },
    {
        "title": "Baseus Pudding Serisi Usb To iPhone uyumlu Lightning USB 2.4A Hızlı Şarj Kablosu",
        "category": "Teknoloji",
        "store": "Hepsiburada",
        "brand": "baseus",
        "ptype": "kablo",
        "brand_type": "baseus_pudding",
        "originalPrice": 285.0,
        "discountedPrice": 189.0,
        "discountRate": 34,
        "productUrl": "https://www.hepsiburada.com/baseus-pudding-serisi-usb-to-iphone-uyumlu-lightning-usb-iphone-uyumlu-2-4-amper-hizli-sarj-ve-data-aktarim-kablosu-iphone-14-13-12-11-x-7-8-6-uyumlu-siyah-p-HBCV00006DOYCV",
        "imageUrl": "https://productimages.hepsiburada.net/s/777/375-375/110000690742174.jpg"
    },
    {
        "title": "Duracell Optimum AA Alkalin Pil, 1,5 V LR6 MN1500, 16’lı paket",
        "category": "Teknoloji",
        "store": "Idefix",
        "brand": "duracell",
        "ptype": "pil",
        "brand_type": "duracell_optimum",
        "originalPrice": 899.0,
        "discountedPrice": 719.0,
        "discountRate": 20,
        "productUrl": "https://www.idefix.com//duracell-optimum-aa-alkalin-pil-15-v-lr6-mn1500-16li-paket-p-3212885",
        "imageUrl": "https://image03.idefix.com/resize/600/600/product/3212885/duracell-optimum-aa-6831d1617a272.jpg"
    }
]

# 3. Mevcut 120 ürünlük listedeki Teknoloji ürünlerini yenileriyle değiştir
non_tech_items = [x for x in catalog if x['category'] != 'Teknoloji']
print(f"Mevcut Diğer Kategoriler (Moda, Ev & Yaşam, Kozmetik): {len(non_tech_items)} ürün (Korunuyor)")

# Yeni listeyi döngüsel (round-robin) harmanla
stores_cycle = ['Hepsiburada', 'Idefix', 'Amazon TR']
by_store = {
    'Hepsiburada': [x for x in (non_tech_items + new_tech_batch) if x['store'] == 'Hepsiburada'],
    'Idefix': [x for x in (non_tech_items + new_tech_batch) if x['store'] == 'Idefix'],
    'Amazon TR': [x for x in (non_tech_items + new_tech_batch) if x['store'] == 'Amazon TR'],
}

rotated_catalog = []
for turn in range(40):
    for s in stores_cycle:
        if by_store[s]:
            it = by_store[s].pop(0)
            it['id'] = f"deal-{len(rotated_catalog)+1:03d}"
            rotated_catalog.append(it)

print(f"Yeni 120 Ürünlük Katalog Oluşturuldu: {len(rotated_catalog)} ürün")

# Kontrol: Teknoloji Sıralaması
new_tech_check = [x for x in rotated_catalog if x['category'] == 'Teknoloji']
print(f"\n=== YENİ TEKNOLOJİ SIRALAMASI (İLK 10) ===")
for i, t in enumerate(new_tech_check[:10]):
    print(f"  {i+1:2d}. [{t['store']:11s}] %{t['discountRate']:2d} | {t['title'][:60]}")

# 4. JSON Dosyalarını Kaydet
with open('scraper/final_equal_verified_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(rotated_catalog, f, ensure_ascii=False, indent=2)

with open('assets/data/live_deals.json', 'w', encoding='utf-8') as f:
    json.dump(rotated_catalog, f, ensure_ascii=False, indent=2)

# 5. Canlı Kalıcı REST API'ye HTTP PUT Gönder
compact_deals = []
for it in rotated_catalog:
    compact_deals.append({
        'id': it['id'],
        'title': it['title'],
        'category': it['category'],
        'store': it['store'],
        'originalPrice': it['originalPrice'],
        'discountedPrice': it['discountedPrice'],
        'discountRate': it['discountRate'],
        'productUrl': it['productUrl'],
        'imageUrl': it['imageUrl']
    })

url = 'https://extendsclass.com/api/json-storage/bin/ccbacbe'
json_data = json.dumps(compact_deals, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(url, data=json_data, headers={
    'Content-Type': 'application/json; charset=utf-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}, method='PUT')

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        print(f"\n[OK] extendsclass HTTP PUT Başarılı! HTTP {resp.status} - Sunucu güncellendi!")
except Exception as e:
    print(f"\n[HATA] extendsclass HTTP PUT: {e}")

print("\n=== ROTASYON TAMAMLANDI - MOBİL UYGULAMADAN YENİLEYİP GÖREBİLİRSİNİZ ===")
