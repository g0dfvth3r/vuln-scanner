import httpx
from colorama import Fore, Style, init
init()

async def run(url, results):
    print('\nCookies:')
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
    
    cookies_results = {}

    for raw_cookie in r.headers.get_list("Set-Cookie"):
        parts = raw_cookie.split(";")
        cookie_name = parts[0].split("=")[0].strip()
        cookie_lower = raw_cookie.lower()
        cookie_flags = {}
        print(f"\n  {cookie_name}")

        for flag in ["secure", "httponly", "samesite"]:
            if flag in cookie_lower:
                cookie_flags[flag] = 'found'
                print(Fore.GREEN + f"    [FOUND]     " + Style.RESET_ALL + f"{flag}")
            else:
                cookie_flags[flag] = 'not found'
                print(Fore.RED + f"    [NOT FOUND]" + Style.RESET_ALL + f" {flag}")
        
        cookies_results[cookie_name] = cookie_flags
    
    results['Cookies'] = cookies_results 