import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "hackathon.db"

DEFAULT_ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change_me")


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name   TEXT NOT NULL,
                email       TEXT NOT NULL UNIQUE,
                phone       TEXT NOT NULL,
                college     TEXT NOT NULL,
                branch      TEXT,
                year        TEXT,
                skills      TEXT,
                github_url  TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS admin_users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token      TEXT PRIMARY KEY,
                admin_id   INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (admin_id) REFERENCES admin_users(id)
            );
            """
        )

        # Table to record notifications sent to admin for new registrations
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_notifications (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id INTEGER NOT NULL,
                created_at     TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (registration_id) REFERENCES registrations(id)
            );
            """
        )

        # Ensure new columns exist in registrations for extended fields
        existing_cols = {col[1] for col in conn.execute("PRAGMA table_info(registrations)").fetchall()}
        alter_stmts = []
        if 'college_id' not in existing_cols:
            alter_stmts.append("ALTER TABLE registrations ADD COLUMN college_id TEXT;")
        if 'team_name' not in existing_cols:
            alter_stmts.append("ALTER TABLE registrations ADD COLUMN team_name TEXT;")
        if 'team_size' not in existing_cols:
            alter_stmts.append("ALTER TABLE registrations ADD COLUMN team_size INTEGER;")
        if 'tshirt_size' not in existing_cols:
            alter_stmts.append("ALTER TABLE registrations ADD COLUMN tshirt_size TEXT;")

        for stmt in alter_stmts:
            try:
                conn.execute(stmt)
            except Exception:
                # ignore if unable to add (already exists or other minor issue)
                pass

        admin = conn.execute(
            "SELECT id FROM admin_users WHERE username = ?",
            (DEFAULT_ADMIN_USERNAME,),
        ).fetchone()

        if admin is None:
            password_hash = pwd_context.hash(DEFAULT_ADMIN_PASSWORD)
            conn.execute(
                "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
                (DEFAULT_ADMIN_USERNAME, password_hash),
            )

        # If ADMIN_PASSWORD env is provided, override the admin user's password hash
        env_admin_pwd = os.getenv("ADMIN_PASSWORD")
        if env_admin_pwd:
            # update password for DEFAULT_ADMIN_USERNAME if exists, else first admin
            admin_row = conn.execute(
                "SELECT id FROM admin_users WHERE username = ?",
                (DEFAULT_ADMIN_USERNAME,),
            ).fetchone()

            if admin_row:
                pwd_hash = pwd_context.hash(env_admin_pwd)
                conn.execute(
                    "UPDATE admin_users SET password_hash = ? WHERE id = ?",
                    (pwd_hash, admin_row["id"]),
                )
            else:
                first = conn.execute(
                    "SELECT id FROM admin_users ORDER BY id LIMIT 1"
                ).fetchone()
                if first:
                    pwd_hash = pwd_context.hash(env_admin_pwd)
                    conn.execute(
                        "UPDATE admin_users SET password_hash = ? WHERE id = ?",
                        (pwd_hash, first["id"]),
                    )

        conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)
