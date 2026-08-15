import sqlite3
from pathlib import Path
DB = Path(__file__).resolve().parents[1] / 'data' / 'hackathon.db'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
try:
    count = conn.execute('SELECT COUNT(*) as c FROM admin_notifications').fetchone()['c']
except Exception as e:
    print('ERROR:', e)
    conn.close()
    raise
print('admin_notifications count =', count)
if count:
    rows = conn.execute('SELECT * FROM admin_notifications ORDER BY id DESC LIMIT 5').fetchall()
    for r in rows:
        print(dict(r))
conn.close()
