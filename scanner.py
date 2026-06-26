import sys
import requests
from colorama import Fore, Style, init
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import importlib.util
import os
from datetime import datetime
import html
import asyncio
import inspect

init()

def print_headers(status_code, headers):
    print('Status code:' + Fore.YELLOW + f' {status_code}\n' + Style.RESET_ALL)
    for key, value in headers.items():
        print(key, ":", value)

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

def generate_html_report(url, results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sections_html = ""
    for section_name, findings in results.items():
        sections_html += f"<h2>{section_name}</h2>"
        sections_html += "<ul>"
        # findings can be a dict or nested dict
        # for now just convert each finding to a list item
        if isinstance(findings, dict):
            for key, value in findings.items():
                if isinstance(value, dict):
                    sections_html += f"<li><strong>{key}</strong><ul>"
                    for flag, flag_value in value.items():
                        color = "green" if flag_value == "found" else "red"
                        sections_html += f'<li style="color:{color}">{flag}: {flag_value}</li>'
                    sections_html += "</ul></li>"
                else:
                    safe_key = html.escape(str(key))
                    safe_value = html.escape(str(value))
                    color = "green" if value in ["found", "safe", "not present"] else "red"
                    sections_html += f'<li style="color:{color}">{safe_key}: {safe_value}</li>'

            sections_html += "</ul>"  # ← outside the loop, closes the section's ul
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Scan Report - {url}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }}
        h1 {{ color: #00ff88; }}
        h2 {{ color: #00aaff; border-bottom: 1px solid #333; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ padding: 4px 0; }}
    </style>
</head>
<body>
    <h1>Vulnerability Scanner Report</h1>
    <p>Target: {url}</p>
    <p>Scanned: {timestamp}</p>
    {sections_html}
</body>
</html>"""

    with open("reports/report.html", "w") as f:
        f.write(html_content)
    
    print(Fore.GREEN + "\n[+] HTML report saved to reports/report.html" + Style.RESET_ALL)

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

async def run_plugins(url, results, plugins):
    tasks = []
    for plugin in plugins:
        if inspect.iscoroutinefunction(plugin.run):
            tasks.append(plugin.run(url, results))
        else:
            plugin.run(url, results)
    
    await asyncio.gather(*tasks)

def scan(url):
    results = {}
    plugins = load_plugins()
    asyncio.run(run_plugins(url, results, plugins))

    with open ("reports/report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    generate_html_report(url, results)

if __name__ == "__main__":
    scan(sys.argv[1])