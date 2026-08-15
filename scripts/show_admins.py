import sqlite3
DB='data/hackathon.db'
conn=sqlite3.connect(DB)
conn.row_factory=sqlite3.Row
rows=conn.execute('SELECT id,username FROM admin_users').fetchall()
for r in rows:
    print(r['id'], r['username'])
conn.close()
