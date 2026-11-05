import subprocess
import re
from bs4 import BeautifulSoup

url = 'https://www.amazon.com.tr/dp/B0D8WP1RLR'
cmd = f'"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --headless=new --disable-gpu --dump-dom "{url}"'
out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
soup = BeautifulSoup(out.decode('utf-8', errors='ignore'), 'html.parser')

print("Title:", soup.title.get_text() if soup.title else 'No Title')
for p in soup.select('.a-price'):
    print(p.get('class'), p.get('data-a-strike'), p.get_text().strip())
