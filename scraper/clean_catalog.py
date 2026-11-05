import json

with open("assets/data/live_deals.json", "r", encoding="utf-8") as f:
    deals = json.load(f)

print(f"Initial deals: {len(deals)}")

cleaned = []
for d in deals:
    did = d['id']
    
    # 1. Update Maybelline
    if did == 'hb-maybelline-sky-high':
        d['imageUrl'] = 'https://productimages.hepsiburada.net/s/777/424-600/110001614800479.jpg'
        d['productUrl'] = 'https://www.hepsiburada.com/lash-sensational-sky-high-maskara-siyah-pm-HB00001B1F32'
        d['title'] = 'Maybelline New York Lash Sensational Sky High Hacim Verici Maskara'
        cleaned.append(d)
        continue

    # 2. Update Karaca
    if did == 'hb-karaca-biogranit':
        d['imageUrl'] = 'https://productimages.hepsiburada.net/s/440/424-600/110000473815720.jpg'
        d['productUrl'] = 'https://www.hepsiburada.com/karaca-gris-bio-granit-7-parca-tencere-seti-pm-HB00000XLLTA'
        d['title'] = 'Karaca Gris Bio Granit 7 Parça Yanmaz Yapışmaz Tencere Seti'
        cleaned.append(d)
        continue

    # 3. Update Logitech G102
    if did == 'hb-logitech-g102':
        d['imageUrl'] = 'https://productimages.hepsiburada.net/s/777/424-600/110000785126667.jpg'
        d['productUrl'] = 'https://www.hepsiburada.com/logitech-910-005823-g102-lightsync-black-8000dpi-6-tus-optik-pm-HB00000V80EP'
        d['title'] = 'Logitech G102 Lightsync RGB 8.000 DPI Kablolu Oyuncu Mouse - Siyah'
        cleaned.append(d)
        continue

    # 4. Remove US Polo shirt with mismatched coat image
    if did == 'hb-us-polo-gomlek':
        continue

    # 5. Remove Spigen case that 404s
    if did == 'amz-B08L5WHFT9':
        continue

    # Keep all other verified deals (Amazon Pantene, Stanley, Anthony Jackson, and 37 Idefix deals)
    cleaned.append(d)

print(f"Final verified deals count: {len(cleaned)}")

# Verify all discountRates >= 50
for d in cleaned:
    assert d['discountRate'] >= 50, f"Discount rate < 50: {d}"

with open("assets/data/live_deals.json", "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

with open("lib/data/live_deals.json", "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

print("Saved cleanly to both assets/data/live_deals.json and lib/data/live_deals.json!")
