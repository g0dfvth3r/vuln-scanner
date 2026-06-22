from colorama import Fore, Style, init
import requests

init()

def run(url, results):
    r = requests.get(url)
    headers = r.headers
    headers_to_check = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    ]
    headers_results = {}
    print('\nSecurity Headers:')
    
    for header in headers_to_check:
        if header in headers:
            print(Fore.GREEN + '[FOUND]' + Style.RESET_ALL + f'     {header}')
            headers_results[header] = 'found'
        else:
            print(Fore.RED + '[NOT FOUND]' + Style.RESET_ALL + f' {header}')
            headers_results[header] = 'not found'

    results["Security_headers"] = headers_results