# Hackathon Registration Website

A student registration website for hackathon events with an admin dashboard to view and export signups.

## Tech Stack

- **Frontend:** HTML, CSS, vanilla JavaScript
- **Web Server:** Node.js (Express)
- **Backend API:** Python (FastAPI)
- **Database:** SQLite
 - **Notifications:** SMTP (email) and Twilio (SMS) optional via env vars

## Project Structure

```
frontend/     # HTML pages, CSS, and client-side JS
backend/      # FastAPI REST API
server/       # Express static server + API proxy
data/         # SQLite database (created on first run)
```

## Setup

### 1. Python Backend

```bash
cd backend
pip install -r requirements.txt
```

Recommended: create and use a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

Optional environment variables (defaults shown):

```bash
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=admin123
```

### 2. Node.js Server

```bash
cd server
npm install
```

The `server` uses `dotenv` and other Node packages — run `npm install` before starting.

## Run Locally

Quick Start (recommended): a helper script `main.py` starts both the FastAPI backend and the static Node server together.

```powershell
# activate venv (PowerShell)
.\.venv\Scripts\Activate.ps1
# from project root
python main.py
```

Or run servers separately:

- Python API (port 8000):

```bash
cd backend
uvicorn main:app --reload --port 8000
```

- Node web server (port 3000):

```bash
cd server
npm start
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Pages

| Page | URL |
|------|-----|
| Landing | `/index.html` |
| Register | `/register.html` |
| Admin Login | `/admin/login.html` |
| Admin Dashboard | `/admin/dashboard.html` |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/register` | Student registration |
| POST | `/api/admin/login` | Admin login |
| POST | `/api/admin/logout` | Admin logout |
| GET | `/api/registrations` | List registrations (admin) |
| GET | `/api/registrations/export` | Export Excel `.xlsx` (admin) |

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs) when the Python server is running.

## Default Admin Credentials

- **Username:** `admin`
- **Password:** `admin123`

Change these via `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables before first run.

## Notes & Extras

- The registration form now includes additional fields: `college_id`, `team_name`, `team_size` (dropdown enforced client-side, recommended server-side validation of 2–4), and `tshirt_size`.
- The export endpoint now produces an Excel file (`registrations.xlsx`) containing the new columns.
- After successful registration the server inserts an `admin_notifications` row and will attempt to send the applicant their Application ID by email and/or SMS if the following environment variables are set:

	- SMTP: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL`
	- Twilio: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM`

- A helper script is included to download the Excel export from the running API (requires admin credentials):

```powershell
.\.venv\Scripts\python scripts\download_export.py admin123
```

## Quick Commands

Create and activate virtualenv (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

Start both servers (helper script):

```powershell
$env:ADMIN_PASSWORD='admin123'
python main.py
```

Or start services individually:

```powershell
# FastAPI API
cd backend
.\.venv\Scripts\python -m uvicorn main:app --reload --port 8000

# Node static server
cd server
npm start
```
