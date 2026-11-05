import subprocess
import re

url = "https://www.hepsiburada.com/ara?q=bluetooth+kulaklik"
cmd = f'"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --headless=new --disable-gpu --dump-dom "{url}"'
print("Running chrome headless...")
out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
html = out.decode('utf-8', errors='ignore')
print("Chrome DOM length:", len(html))
found_paths = re.findall(r'href=["\'](/[^"\']*-p(?:m)?-[a-zA-Z0-9]+[^"\']*)["\']', html)
print("Found PDP links via Chrome:", len(found_paths))
if found_paths:
    print("Sample:", found_paths[:3])
