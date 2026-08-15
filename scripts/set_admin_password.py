import sqlite3
import sys
from passlib.context import CryptContext

DB = 'data/hackathon.db'
ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def set_password(password: str):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Prefer updating 'admin' user if present
    row = cur.execute("SELECT id, username FROM admin_users WHERE username = ?", ("admin",)).fetchone()
    if row is None:
        # fallback to first admin user
        row = cur.execute("SELECT id, username FROM admin_users ORDER BY id LIMIT 1").fetchone()

    if row is None:
        print("No admin users found in DB.")
        conn.close()
        return

    password_hash = ctx.hash(password)
    cur.execute("UPDATE admin_users SET password_hash = ? WHERE id = ?", (password_hash, row['id']))
    conn.commit()
    print(f"Updated password for admin user: {row['username']}")
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: set_admin_password.py <new_password>")
        raise SystemExit(1)
    set_password(sys.argv[1])
