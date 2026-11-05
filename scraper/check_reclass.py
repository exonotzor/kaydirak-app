import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

with open('assets/data/live_deals.json', 'r', encoding='utf-8') as f:
    deals = json.load(f)

cosmetic_kw = ['krem', 'serum', 'losyon', 'nemlendirici', 'hydro boost', 'nivea', 'neutrogena', 'loreal', 'parfüm', 'parfum', 'deodorant', 'şampuan', 'sampuan', 'maske', 'makyaj', 'ruj', 'rimel', 'maskara', 'cilt', 'bakım yağı', 'tonik', 'güneş kremi', 'skinmaster', 'yüz temizleme', 'dudak', 'kolonya', 'epilatör', 'ağda', 'oje', 'vücut spreyi', 'eyeliner', 'fondöten']
fashion_kw = ['yelek', 'mont', 'şort', 'sort', 'kapri', 'pantolon', 't-shirt', 'tişört', 'kazak', 'hırka', 'sweatshirt', 'swetşört', 'ayakkabı', 'bot', 'çorap', 'ceket', 'gömlek', 'polar', 'tayt', 'içlik', 'boxer', 'kaban', 'atlet', 'elbise', 'etek', 'takım', 'benetton', 'adidas', 'millet', 'tommy', 'jack wolfskin', 'puma', 'nike', 'skechers']
home_kw = ['buzluk', 'termos', 'fincan', 'tava', 'tencere', 'tabak', 'nevresim', 'yastık', 'yorgan', 'havlu', 'deterjan', 'yumuşatıcı', 'sabun', 'oda spreyi', 'cooler', 'matara']

reclassed = []
for d in deals:
    raw_cat = d['category']
    title_lower = d['title'].lower()
    final_cat = raw_cat
    if any(k in title_lower for k in cosmetic_kw):
        final_cat = 'Kozmetik'
    elif any(k in title_lower for k in fashion_kw):
        final_cat = 'Moda'
    elif any(k in title_lower for k in home_kw):
        final_cat = 'Ev & Yaşam'
    
    if final_cat != raw_cat:
        reclassed.append((raw_cat, final_cat, d['title']))

print(f"Total reclassified: {len(reclassed)}")
for r in reclassed:
    print(f"[{r[0]}] -> [{r[1]}]: {r[2]}")
