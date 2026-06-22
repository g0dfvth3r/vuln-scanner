import requests
from colorama import Fore, Style, init

def run(url, results):
    print('\nRedirects')
    redirect_results = {}
    for i in [ 'next', 'redirect', 'url', 'return', 'returnUrl', 'goto', 'target', 'redir']:
        target = url + '/login?' + i + '=https://evil.com'
        r = requests.get(target)
        if r.url.startswith('https://evil.com') and len(r.history) > 0:
            redirect_results[i] = 'vulnerable'
            print(Fore.RED + f'[VULNERABLE] {i} redirected to evil.com' + Style.RESET_ALL)
        else:
            redirect_results[i] = 'safe'
            print(Fore.GREEN + f'[SAFE] {i}' + Style.RESET_ALL)
    results['Redirects'] = redirect_results