"""
Authentication & Authorization Module
Handles bcrypt password hashing, session tokens, and admin route protection.
"""

import uuid
from fastapi import Header, HTTPException, status
from passlib.context import CryptContext

from database import get_connection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_admin_credentials(username: str, password: str) -> int | None:
    """Verifies admin username and password against database hashes."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, password_hash FROM admin_users WHERE username = ?",
            (username,),
        ).fetchone()

        if row is None:
            return None

        if not pwd_context.verify(password, row["password_hash"]):
            return None

        return row["id"]


def create_session(admin_id: int) -> str:
    """Generates and persists a unique session token for an authenticated admin."""
    token = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO sessions (token, admin_id) VALUES (?, ?)",
            (token, admin_id),
        )
        conn.commit()
    return token


def delete_session(token: str) -> None:
    """Deletes an active admin session token."""
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()


def get_admin_id_from_token(token: str | None) -> int | None:
    """Looks up the admin ID associated with a session token."""
    if not token:
        return None

    with get_connection() as conn:
        row = conn.execute(
            "SELECT admin_id FROM sessions WHERE token = ?",
            (token,),
        ).fetchone()

        if row is None:
            return None

        return row["admin_id"]


def require_admin(authorization: str | None = Header(default=None)) -> int:
    """FastAPI Dependency: Enforces that incoming request has a valid admin Bearer token."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()

    admin_id = get_admin_id_from_token(token)
    if admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin session",
        )

    return admin_id
