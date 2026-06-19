# Vulnerability Scanner

A Python-based web vulnerability scanner built as a portfolio project.

## What it does
- Fetches HTTP response headers from any URL
- Checks for missing security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- Checks cookie flags (Secure, HttpOnly, SameSite)
- Color coded terminal output
- Checks open redirects 

## Usage
```bash
pip install requests colorama
python3 scanner.py https://example.com
```
