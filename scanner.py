import sys
import requests

r = requests.get(f'https://{sys.argv[1]}')
print(r.status_code, r.headers)