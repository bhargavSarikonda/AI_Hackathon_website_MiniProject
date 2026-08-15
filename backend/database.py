"""
Database Management Module
Handles SQLite connection lifecycle, schema initialization, and admin credentials.
"""

import os
import sqlite3
from pathlib import Path
from typing import Any

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
    """Creates and returns a SQLite database connection with row factory enabled."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Initializes tables and default admin user if they do not exist."""
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
                college_id  TEXT,
                team_name   TEXT,
                team_size   INTEGER,
                tshirt_size TEXT,
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

            CREATE TABLE IF NOT EXISTS admin_notifications (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id INTEGER NOT NULL,
                created_at      TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (registration_id) REFERENCES registrations(id)
            );
            """
        )

        # Seed or update default admin user
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
        else:
            env_admin_pwd = os.getenv("ADMIN_PASSWORD")
            if env_admin_pwd and env_admin_pwd != "change_me":
                pwd_hash = pwd_context.hash(env_admin_pwd)
                conn.execute(
                    "UPDATE admin_users SET password_hash = ? WHERE id = ?",
                    (pwd_hash, admin["id"]),
                )

        conn.commit()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any]:
    """Converts a sqlite3.Row instance into a standard Python dictionary."""
    return dict(row) if row is not None else {}
