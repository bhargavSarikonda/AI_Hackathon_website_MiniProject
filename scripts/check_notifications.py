import sqlite3
from pathlib import Path
DB = Path(__file__).resolve().parents[1] / 'data' / 'hackathon.db'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT * FROM admin_notifications ORDER BY id DESC LIMIT 5').fetchall()
for r in rows:
    print(dict(r))
conn.close()
