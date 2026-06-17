import sys
import requests

url = sys.argv[1]
if not url.startswith("http"):
    url = "https://" + url

r = requests.get(url)
print(f"Status code: {r.status_code}\n")
headers = r.headers

for key, value in headers.items():
    print(key, ":", value)
