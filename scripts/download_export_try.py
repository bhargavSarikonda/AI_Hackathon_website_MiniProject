import json
import urllib.request

BASE = "http://127.0.0.1:8000"

login_url = BASE + "/api/admin/login"
headers = {"Content-Type": "application/json"}

passwords = ["change_me", "admin123", "admin", "password", "hackathon"]
token = None
for pwd in passwords:
    login_payload = {"username": "admin", "password": pwd}
    req = urllib.request.Request(login_url, data=json.dumps(login_payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.load(resp)
            token = body.get('token')
            print('Login succeeded with password:', pwd)
            break
    except Exception as e:
        print('Tried', pwd, '->', e)

if not token:
    print('Could not login with tested passwords; update the script with correct admin password.')
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
