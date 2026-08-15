import csv
import io
import os
import sqlite3
import smtplib
from email.message import EmailMessage
from io import BytesIO
from base64 import b64encode

import openpyxl
from openpyxl import Workbook
import requests

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import StreamingResponse

import auth
from database import get_connection, init_db, row_to_dict
from models import (
    AdminLoginRequest,
    AdminLoginResponse,
    MessageResponse,
    RegistrationCreate,
    RegistrationResponse,
)

app = FastAPI(title="Hackathon Registration API", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post(
    "/api/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_student(payload: RegistrationCreate) -> RegistrationResponse:
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO registrations (
                    full_name, email, phone, college, branch, year, skills, github_url, college_id, team_name, team_size, tshirt_size
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.full_name.strip(),
                    payload.email.lower().strip(),
                    payload.phone.strip(),
                    payload.college.strip(),
                    payload.branch.strip() if payload.branch else None,
                    payload.year.strip() if payload.year else None,
                    payload.skills.strip() if payload.skills else None,
                    payload.github_url.strip() if payload.github_url else None,
                    payload.college_id.strip() if getattr(payload, 'college_id', None) else None,
                    payload.team_name.strip() if getattr(payload, 'team_name', None) else None,
                    int(payload.team_size) if getattr(payload, 'team_size', None) else None,
                    payload.tshirt_size.strip() if getattr(payload, 'tshirt_size', None) else None,
                ),
            )
            conn.commit()
            registration_id = cursor.lastrowid

            # Record notification for admin (so admin can see which registration triggered the message)
            try:
                conn.execute(
                    "INSERT INTO admin_notifications (registration_id) VALUES (?)",
                    (registration_id,)
                )
                conn.commit()
            except Exception:
                # non-fatal, keep going
                pass

            # Send application id to user via email and SMS (if configured)
            try:
                row = conn.execute(
                    "SELECT * FROM registrations WHERE id = ?",
                    (registration_id,),
                ).fetchone()
                data = row_to_dict(row)
                application_id = data.get("id")
                email_addr = data.get("email")
                phone = data.get("phone")

                # Compose message
                subject = "Your Innovate AI Hackathon 2026 Application ID"
                body = f"Thank you for registering for Innovate AI Hackathon 2026. Your Application ID is: {application_id}. Keep this for your records."

                # Send email if SMTP configured
                smtp_host = os.getenv("SMTP_HOST")
                smtp_port = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else None
                smtp_user = os.getenv("SMTP_USER")
                smtp_pass = os.getenv("SMTP_PASS")
                from_addr = os.getenv("FROM_EMAIL", smtp_user)

                if smtp_host and smtp_user and smtp_pass and email_addr:
                    try:
                        msg = EmailMessage()
                        msg["Subject"] = subject
                        msg["From"] = from_addr
                        msg["To"] = email_addr
                        msg.set_content(body)

                        server = smtplib.SMTP(smtp_host, smtp_port or 587)
                        server.starttls()
                        server.login(smtp_user, smtp_pass)
                        server.send_message(msg)
                        server.quit()
                    except Exception:
                        # swallow email errors for now
                        pass

                # Send SMS via Twilio if configured
                twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
                twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
                twilio_from = os.getenv("TWILIO_FROM")
                if twilio_sid and twilio_token and twilio_from and phone:
                    try:
                        url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
                        payload = {
                            "To": phone,
                            "From": twilio_from,
                            "Body": body,
                        }
                        auth = (twilio_sid, twilio_token)
                        requests.post(url, data=payload, auth=auth, timeout=10)
                    except Exception:
                        pass

            except Exception:
                # non-fatal; registration succeeded even if notification failed
                pass

            # ensure row is fetched for response (if not already fetched above)
            try:
                row
            except NameError:
                row = conn.execute(
                    "SELECT * FROM registrations WHERE id = ?",
                    (registration_id,),
                ).fetchone()
    except sqlite3.IntegrityError as exc:
        if "UNIQUE constraint failed: registrations.email" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed",
        ) from exc

    return RegistrationResponse(**row_to_dict(row))


@app.post("/api/admin/login", response_model=AdminLoginResponse)
def admin_login(payload: AdminLoginRequest) -> AdminLoginResponse:
    admin_id = auth.verify_admin_credentials(payload.username, payload.password)
    if admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = auth.create_session(admin_id)
    return AdminLoginResponse(token=token, username=payload.username)


@app.post("/api/admin/logout", response_model=MessageResponse)
def admin_logout(
    authorization: str | None = Header(default=None),
    _: int = Depends(auth.require_admin),
) -> MessageResponse:
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()

    if token:
        auth.delete_session(token)

    return MessageResponse(message="Logged out successfully")


@app.get("/api/registrations", response_model=list[RegistrationResponse])
def list_registrations(_: int = Depends(auth.require_admin)) -> list[RegistrationResponse]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM registrations ORDER BY created_at DESC"
        ).fetchall()

    return [RegistrationResponse(**row_to_dict(row)) for row in rows]


@app.get("/api/registrations/export")
def export_registrations(_: int = Depends(auth.require_admin)) -> StreamingResponse:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM registrations ORDER BY created_at DESC"
        ).fetchall()
    # Create Excel workbook in-memory
    wb = Workbook()
    ws = wb.active
    ws.title = "Registrations"

    headers = [
        "ID",
        "Full Name",
        "Email",
        "Phone",
        "College",
        "College ID",
        "Branch",
        "Year",
        "Team Name",
        "Team Size",
        "T-shirt Size",
        "Skills",
        "GitHub URL",
        "Registered At",
    ]

    ws.append(headers)

    for row in rows:
        data = row_to_dict(row)
        ws.append(
            [
                data.get("id"),
                data.get("full_name"),
                data.get("email"),
                data.get("phone"),
                data.get("college"),
                data.get("college_id") or "",
                data.get("branch") or "",
                data.get("year") or "",
                data.get("team_name") or "",
                data.get("team_size") if data.get("team_size") is not None else "",
                data.get("tshirt_size") or "",
                data.get("skills") or "",
                data.get("github_url") or "",
                data.get("created_at"),
            ]
        )

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    return StreamingResponse(
        iter([bio.read()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=registrations.xlsx"},
    )
