from curl_cffi import requests
from bs4 import BeautifulSoup

session = requests.Session(impersonate="chrome124", verify=False)
# 1. Search page sets Akamai cookies
s_url = "https://www.hepsiburada.com/ara?q=kulaklik"
r1 = session.get(s_url, timeout=10)
print("Search page status:", r1.status_code, "Cookies:", len(session.cookies))

# 2. PDP visit with session cookies
pdp_url = "https://www.hepsiburada.com/redmi-buds-6-play-siyah-kulakici-kulaklik-tws-xiaomi-turkiye-garantili-p-HBCV000072PXK3"
r2 = session.get(pdp_url, timeout=10)
print("PDP status:", r2.status_code, "Length:", len(r2.text))
soup = BeautifulSoup(r2.text, 'html.parser')
h1 = soup.find('h1')
print("PDP Title:", h1.get_text().strip() if h1 else 'None')
