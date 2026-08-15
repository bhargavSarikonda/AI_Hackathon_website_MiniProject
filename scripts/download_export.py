import json
import urllib.request

BASE = "http://127.0.0.1:8000"

# Login as admin (default username 'admin', password from env or 'change_me')
login_url = BASE + "/api/admin/login"
headers = {"Content-Type": "application/json"}

import os

password = os.getenv('ADMIN_PASSWORD')
if not password:
    import sys
    if len(sys.argv) > 1:
        password = sys.argv[1]

if not password:
    print('Provide admin password via ADMIN_PASSWORD env or first arg')
    raise SystemExit(1)

login_payload = {"username": "admin", "password": password}
req = urllib.request.Request(login_url, data=json.dumps(login_payload).encode('utf-8'), headers=headers, method='POST')
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.load(resp)
        token = body.get('token')
        print('Got token')
except Exception as e:
    print('Login error:', e)
    raise SystemExit(1)

export_url = BASE + "/api/registrations/export"
req2 = urllib.request.Request(export_url, headers={"Authorization": f"Bearer {token}"})
try:
    with urllib.request.urlopen(req2, timeout=20) as resp:
        data = resp.read()
        with open('registrations_export.xlsx', 'wb') as f:
            f.write(data)
        print('Saved registrations_export.xlsx')
except Exception as e:
    print('Export error:', e)
