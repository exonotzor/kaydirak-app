import socket
import requests
import urllib3

urllib3.disable_warnings()

hosts = [
    'www.hepsiburada.com',
    'api.hepsiburada.com',
    'gw.hepsiburada.com',
    'sf-gateway.hepsiburada.com',
    'app.hepsiburada.com',
    'mobile.hepsiburada.com',
    'listing.hepsiburada.com',
    'search.hepsiburada.com',
]

for h in hosts:
    try:
        ip = socket.gethostbyname(h)
        print(f"{h} -> {ip}")
    except Exception as e:
        print(f"{h} -> NOT RESOLVED")
