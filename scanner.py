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

headers_to_check = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options"
]
print('\nSecurity Headers:')
for header in headers_to_check:
    if header in headers:
        print(f'[FOUND]     {header}')
    else:
        print(f'[NOT FOUND] {header}')
