import subprocess

url = "https://www.hepsiburada.com/ara?q=kulaklik"
cmd = f'"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --headless=new --disable-gpu --virtual-time-budget=5000 --dump-dom "{url}"'
try:
    out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
    print("Length with virtual time budget:", len(out))
    print("Contains 'Redmi' or 'fiyat'?", 'fiyat' in out.lower(), 'redmi' in out.lower())
    if len(out) > 5000:
        print("Text sample:", out[1000:1500])
except Exception as e:
    print("Error:", e)
