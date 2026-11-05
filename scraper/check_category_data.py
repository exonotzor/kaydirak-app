import requests
import urllib3

urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get('https://www.idefix.com/kulakliklar-c-2313670940', headers=headers, verify=False)
print("status:", r.status_code, "len:", len(r.text), "has __NEXT_DATA__:", '__NEXT_DATA__' in r.text)
