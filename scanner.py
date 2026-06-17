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

cookie_header_to_check = [
    " secure",
    " httponly",
    " samesite"
]

print('\nCookies:')
for raw_cookie in r.raw.headers.getlist("Set-Cookie"):
    parts = raw_cookie.split(";")
    cookie_name = parts[0].split("=")[0].strip()
    cookie_lower = raw_cookie.lower()
    
    print(f"\n  {cookie_name}")
    
    for flag in ["secure", "httponly", "samesite"]:
        if flag in cookie_lower:
            print(f"    [FOUND]     {flag}")
        else:
            print(f"    [NOT FOUND] {flag}")
    