import sys
import requests
from colorama import Fore, Style, init

init()

url = sys.argv[1]
if not url.startswith("http"):
    url = "https://" + url

r = requests.get(url)
print('Status code:' + Fore.YELLOW + f' {r.status_code}\n' + Style.RESET_ALL)
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
        print(Fore.GREEN + '[FOUND]' + Style.RESET_ALL + f'     {header}')
    else:
        print(Fore.RED + '[NOT FOUND]' + Style.RESET_ALL + f' {header}')

print('\nCookies:')
for raw_cookie in r.raw.headers.getlist("Set-Cookie"):
    parts = raw_cookie.split(";")
    cookie_name = parts[0].split("=")[0].strip()
    cookie_lower = raw_cookie.lower()
    
    print(f"\n  {cookie_name}")
    
    for flag in ["secure", "httponly", "samesite"]:
        if flag in cookie_lower:
            print(Fore.GREEN + f"    [FOUND]     " + Style.RESET_ALL + f"{flag}")
        else:
            print(Fore.RED + f"    [NOT FOUND]" + Style.RESET_ALL + f" {flag}")
    