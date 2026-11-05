import subprocess

url = "https://www.hepsiburada.com/ara?q=kulaklik"
cmd = f'"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --headless=new --disable-gpu --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" --dump-dom "{url}"'
try:
    out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
    print("Length:", len(out))
    print("Text head:", out[:300])
except Exception as e:
    print("Error:", e)
