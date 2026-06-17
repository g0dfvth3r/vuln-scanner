import sys
import requests

url = sys.argv[1]
if not url.startswith("http"):
    url = "https://" + url
r = requests.get(url)
print(r.status_code, r.headers)
