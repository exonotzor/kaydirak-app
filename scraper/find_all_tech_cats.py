import requests
import urllib3
import json
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

with open('scraper/idefix_all_categories.json', 'r', encoding='utf-8') as f:
    cats = json.load(f)

# Find all categories related to electronics, computers, phones, accessories, sound, photo, etc.
tech_cats = []
for c in cats:
    u = c['url'].lower()
    n = c['name'].lower()
    if any(k in u or k in n for k in ['elektronik', 'teknoloji', 'telefon', 'bilgisayar', 'tablet', 'kulaklik', 'kulaklık', 'sarj', 'şarj', 'kablo', 'powerbank', 'gaming', 'oyuncu', 'hoparlor', 'hoparlör', 'kamera', 'foto', 'saat', 'akilli', 'akıllı', 'aksesuar', 'tv', 'ses', 'goruntu', 'görüntü', 'konsol', 'joystick', 'mouse', 'klavye', 'hafiza', 'hafıza', 'usb', 'modem', 'router']):
        # exclude fashion watches or fashion accessories
        if not any(k in u for k in ['kadin-aksesuar', 'erkek-aksesuar', 'taki', 'canta', 'ayakkabi', 'bebek', 'mama', 'oto-koltugu']):
            tech_cats.append(c)

print(f"Total targeted tech categories: {len(tech_cats)}")
for c in tech_cats:
    print(f"  {c['name']} -> {c['url']}")
