import sys
import requests
from colorama import Fore, Style, init
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

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

def check_cors(url):
    r = requests.get(url, headers= {"Origin": "https://evil.com"})
    headers = r.headers
    print('\nCORS:')
    if "Access-Control-Allow-Origin" in headers:
        value = headers["Access-Control-Allow-Origin"]
        print(value)
        if value == '*':
            print(Fore.RED + 'Warning, Access-Control-Allow-Origin set to *. This is Dangerous' + Style.RESET_ALL)
    else:
        print(Fore.GREEN + "[SAFE] " + Style.RESET_ALL + "Access-Control-Allow-Origin not present")
    if "Access-Control-Allow-Credentials" in headers:
        if headers["Access-Control-Allow-Credentials"].lower() == "true":    
            print(Fore.RED + 'Warning, Access-Control-Allow-Credentials is set to True. This is Dangerous' + Style.RESET_ALL)
def check_redirects(url):
    print('\nRedirects')
    for i in [ 'next', 'redirect', 'url', 'return', 'returnUrl', 'goto', 'target', 'redir']:
        target = url + '/login?' + i + '=https://evil.com'
        r = requests.get(target)
        if r.url.startswith('https://evil.com') and len(r.history) > 0:
            print(Fore.RED + f'[VULNERABLE] {i} redirected to evil.com' + Style.RESET_ALL)
        else:
            print(Fore.GREEN + f'[SAFE] {i}' + Style.RESET_ALL)

def get_links(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a")
    full_urls = []
    for link in links:
        href = link.get("href")
        
        if href is None:
            continue
        
        if href.startswith("mailto:") or href.startswith("javascript:") or href == "#":
            continue
        
        full_url = urljoin(url, href)
        full_urls.append(full_url)
    
    return full_urls

def crawl(start_url, max_depth=2):
    queue = [(start_url,0)]
    visited = set()

    while queue:
        url, depth = queue.pop(0)

        if url in visited:
            continue
        if depth > max_depth:
            continue

        visited.add(url)
        new_links = get_links(url)

        for new_link in new_links:
            if urlparse(new_link).netloc == urlparse(start_url).netloc:
                queue.append((new_link,depth +1))

    return visited

def scan(url):
    if not url.startswith("http"):
        target = "https://" + url
    else:
        target = url
    r = requests.get(target)
    print_headers(r.status_code, r.headers)
    check_security_headers(r.headers)
    check_cookies(r.raw)
    check_cors(target)
    check_redirects(target)
    discovered = crawl(target)
    print(f"\nCrawled {len(discovered)} pages:")
    for page in discovered:
        print(f"  {page}")

if __name__ == "__main__":
    scan(sys.argv[1])