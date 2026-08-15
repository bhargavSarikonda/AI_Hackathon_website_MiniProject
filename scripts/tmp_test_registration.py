import json
import urllib.request
import time

url = "http://127.0.0.1:8000/api/register"
headers = {"Content-Type": "application/json"}

ts = int(time.time())
email = f"testuser+autotest_{ts}@example.com"

data = {
    "full_name": "Test User",
    "email": email,
    "phone": "1234567890",
    "college": "Test University",
    "branch": "Computer Science",
    "year": "3rd Year",
    "skills": "Python, ML",
    "github_url": "https://github.com/testuser",
    "college_id": "TU12345",
    "team_name": "Alpha Team",
    "team_size": 2,
    "tshirt_size": "M"
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode('utf-8')
        print('Status:', resp.status)
        print(body)
except Exception as e:
    print('Error:', e)
