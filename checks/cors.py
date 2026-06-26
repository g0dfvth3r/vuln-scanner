import httpx
from colorama import Fore, Style, init
init()

async def run(url, results):
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers= {"Origin": "https://evil.com"})
    headers = r.headers
    cors_results = {}
    print('\nCORS:')
    if "Access-Control-Allow-Origin" in headers:
        value = headers["Access-Control-Allow-Origin"]
        print(value)
        if value == '*':
            cors_results["Access-Control-Allow-Origin"] = 'vulnerable'
            print(Fore.RED + 'Warning, Access-Control-Allow-Origin set to *. This is Dangerous' + Style.RESET_ALL)
        else:
            cors_results["Access-Control-Allow-Origin"] = value
            print(Fore.GREEN + f"[SAFE] value is {value} " + Style.RESET_ALL )
    else:
        cors_results["Access-Control-Allow-Origin"] = 'not present'
        print(Fore.GREEN + "[SAFE] " + Style.RESET_ALL + "Access-Control-Allow-Origin not present")
    if "Access-Control-Allow-Credentials" in headers:
        if headers["Access-Control-Allow-Credentials"].lower() == "true":
            cors_results["Access-Control-Allow-Credentials"] = 'vulnerable'
            print(Fore.RED + 'Warning, Access-Control-Allow-Credentials is set to True. This is Dangerous' + Style.RESET_ALL)

    results["CORS"] = cors_results
