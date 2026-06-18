import sys
import requests
from colorama import Fore, Style, init

init()

def print_headers(status_code, headers):
    print('Status code:' + Fore.YELLOW + f' {status_code}\n' + Style.RESET_ALL)
    for key, value in headers.items():
        print(key, ":", value)

def check_security_headers(headers):
    headers_to_check = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    ]

    print('\nSecurity Headers:')
    for header in headers_to_check:
        if header in headers:
            print(Fore.GREEN + '[FOUND]' + Style.RESET_ALL + f'     {header}')
        else:
            print(Fore.RED + '[NOT FOUND]' + Style.RESET_ALL + f' {header}')

def check_cookies(raw):
    print('\nCookies:')
    for raw_cookie in raw.headers.getlist("Set-Cookie"):
        parts = raw_cookie.split(";")
        cookie_name = parts[0].split("=")[0].strip()
        cookie_lower = raw_cookie.lower()

        print(f"\n  {cookie_name}")

        for flag in ["secure", "httponly", "samesite"]:
            if flag in cookie_lower:
                print(Fore.GREEN + f"    [FOUND]     " + Style.RESET_ALL + f"{flag}")
            else:
                print(Fore.RED + f"    [NOT FOUND]" + Style.RESET_ALL + f" {flag}")

def scan(url):
    if not url.startswith("http"):
        target = "https://" + url
    else:
        target = url
    r = requests.get(target)
    print_headers(r.status_code, r.headers)
    check_security_headers(r.headers)
    check_cookies(r.raw)

if __name__ == "__main__":
    scan(sys.argv[1])