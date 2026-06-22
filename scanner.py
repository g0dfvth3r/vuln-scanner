import sys
import requests
from colorama import Fore, Style, init
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import importlib.util
import os

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

    results = {}
    print('\nSecurity Headers:')
    
    for header in headers_to_check:
        if header in headers:
            print(Fore.GREEN + '[FOUND]' + Style.RESET_ALL + f'     {header}')
            results[header] = 'found'
        else:
            print(Fore.RED + '[NOT FOUND]' + Style.RESET_ALL + f' {header}')
            results[header] = 'not found'

    return results

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

def check_xss(url):
    print('\nXSS')
    payloads = ['<script>alert("test")</script>',
    '<img src="x" onerror="alert("XSS")">',
    '<svg/onload=alert("XSS")>'
    ]
    
    session = requests.Session()
    r = session.get("http://localhost/login.php")
    soup = BeautifulSoup(r.text, "html.parser")
    token_input = soup.find("input", {"name": "user_token"})
    user_token = token_input.get("value")
    session.post("http://localhost/login.php", data={
        "username": "admin",
        "password": "password",
        "Login": "Login",
        "user_token": user_token
    })
    r = session.get("http://localhost/security.php")
    soup = BeautifulSoup(r.text, "html.parser")
    token_input = soup.find("input", {"name": "user_token"})
    security_token = token_input.get("value")

    session.post("http://localhost/security.php", data={
        "security": "low",
        "seclev_submit": "Submit",
        "user_token": security_token
    })
    results = {}

    for payload in payloads:
        r = session.get(url, params={"name": payload})
        if payload in r.text:
            results[payload] = 'vulnerable'
            print(Fore.RED + f'XSS Detected with payload: {payload}' + Style.RESET_ALL)
        else:
            results[payload] = 'safe'
            print(Fore.GREEN + f'NO XSS Detected with payload: {payload}' + Style.RESET_ALL)
    
    return results

def check_sqli(url):
    print('\nSQLI')
    session = requests.Session()
    r = session.get("http://localhost/login.php")
    soup = BeautifulSoup(r.text, "html.parser")
    token_input = soup.find("input", {"name": "user_token"})
    user_token = token_input.get("value")
    session.post("http://localhost/login.php",data={
        "username": "admin",
        "password": "password",
        "Login": "Login",
        "user_token": user_token
    })
    
    r = session.get("http://localhost/security.php")
    soup = BeautifulSoup(r.text, "html.parser")
    token_input = soup.find("input", {"name": "user_token"})
    security_token = token_input.get("value")
    session.post("http://localhost/security.php", data={
        "security": "low",
        "seclev_submit": "Submit",
        "user_token": security_token
    })

    payloads = [
        "'",
        '"',
        "' OR '1'='1",
        "1' OR '1'='1"
    ]

    errors = [
        'SQL syntax',
        'mysql_fetch',
        'ORA-01756',
        'PostgreSQL',
        'SQLite3::'
    ]
    results = {}
    
    for payload in payloads:
        r = session.get(url, params={
            "id": payload,
            "Submit": "Submit"
        })
        found = False
        for error in errors:
            if error in r.text:
                found = True
                break
        if found:
            results[payload] = 'vulnerable'
            print(Fore.RED + f"[VULNERABLE] {payload}" + Style.RESET_ALL)
        else:
            results[payload] = 'safe'
            print(Fore.GREEN + f"[SAFE] {payload}" + Style.RESET_ALL)

    return results

def load_plugins(checks_dir="checks"):
    plugins = []
    for filename in os.listdir(checks_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(checks_dir, filename)
            spec = importlib.util.spec_from_file_location(filename, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugins.append(module)
    return plugins

def scan(url):
    results = {}
    plugins = load_plugins()

    for plugin in plugins:
        plugin.run(url, results)

    with open ("reports/report.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    scan(sys.argv[1])