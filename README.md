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
AI_Hackathon_website_MiniProject/
├── backend/                              # FastAPI Python Backend
│   ├── rag/                              # Modular RAG AI Chatbot Package
│   │   ├── __init__.py                   # Package exports & public API
│   │   ├── ingestion.py                  # Stage 1: Document parser & dataset reader
│   │   ├── chunker.py                    # Stage 2: Semantic chunker & metadata tagger
│   │   ├── embedder.py                   # Stage 3: High-dimensional vector embedder
│   │   ├── vector_db.py                  # Stage 4: ChromaDB vector database store
│   │   ├── retriever.py                  # Stage 4.5: Hybrid vector search retriever
│   │   ├── generator.py                  # Stage 5: Grounded answer synthesis & LLM integration
│   │   ├── knowledge_base.py             # Rulebook dataset ingestor & metadata
│   │   ├── router.py                     # FastAPI Chat endpoints (/api/chat)
│   │   ├── schemas.py                    # Pydantic chat request/response models
│   │   └── service.py                    # RAG singleton service orchestrator
│   ├── auth.py                           # Admin session verification & auth
│   ├── database.py                       # SQLite database manager & table schemas
│   ├── main.py                           # FastAPI application entrypoint
│   ├── models.py                         # Pydantic schemas for registrations & admin
│   └── requirements.txt                  # Python package dependencies
├── data/                                 # Persistent Database & Vector Stores
│   ├── chroma_db/                        # ChromaDB persistent vector database
│   ├── hackathon.db                      # SQLite database file
│   └── Innovate_AI_Hackathon_Rulebook_DataSet.docx # Official Hackathon Rulebook Dataset
├── frontend/                             # Client-side Static Web Application
│   ├── admin/                            # Admin Portal
│   │   ├── dashboard.html                # Admin dashboard to search & export data
│   │   └── login.html                    # Admin login page
│   ├── assets/                           # Media & Visual Assets
│   │   ├── company-logos/                # Sponsor & partner logos
│   │   ├── background.svg                # Background graphic
│   │   └── logo.svg                      # Event & animated Chatbot logo
│   ├── css/                              # Stylesheets
│   │   ├── chatbot.css                   # Glassmorphic floating AI Chatbot styles
│   │   └── style.css                     # Global design system & layout styles
│   ├── js/                               # Client-side Logic
│   │   ├── admin.js                      # Admin authentication & dashboard logic
│   │   ├── chatbot.js                    # Floating AI Chatbot UI widget & API client
│   │   ├── login.js                      # User OTP authentication logic
│   │   └── register.js                   # Registration form validation & submission
│   ├── index.html                        # Landing page (event info, timeline, rules)
│   ├── login.html                        # Participant OTP login page
│   ├── register.html                     # Student registration form
│   └── user-dashboard.html               # Participant post-login dashboard
├── scripts/                              # Utility & Management Scripts
│   ├── check_notifications.py            # Check registration notification records
│   ├── check_notifications_verbose.py    # Detailed notification log inspector
│   ├── download_export.py                # Helper script to download Excel export
│   ├── download_export_try.py            # Diagnostic export test script
│   ├── set_admin_password.py             # Reset/update admin credentials
│   ├── show_admins.py                    # Display admin user accounts
│   └── tmp_test_registration.py          # Script to simulate test registration
├── server/                               # Node.js Express Web Server
│   ├── node_modules/                     # Node.js dependencies
│   ├── package.json                      # Node packages & start scripts
│   ├── package-lock.json                 # Dependency lockfile
│   └── server.js                         # Static file server & API proxy (/api/* -> :8000)
├── .env.example                          # Example environment variables template
├── .env                                  # Local environment configuration
├── .gitignore                            # Git ignored files & patterns
├── main.py                               # Root launcher script (runs Python + Node concurrently)
└── README.md                             # Project documentation
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
set OPENAI_API_KEY=your_openai_api_key   # Optional: for generative LLM RAG mode
set GEMINI_API_KEY=your_gemini_api_key   # Optional: for Google Gemini RAG mode
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
| User Login | `/login.html` |
| User Dashboard | `/user-dashboard.html` |
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
| POST | `/api/chat` | RAG AI Chatbot query processing |
| GET | `/api/chat/faq` | Curated FAQ quick-start prompts |

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs) when the Python server is running.

## 🤖 RAG AI Chatbot Architecture

The AI Chatbot is built with a modular 5-stage Retrieval-Augmented Generation (RAG) pipeline grounded in the official event rulebook:

```
[Source Data (.docx)] 
       │
       ▼
[1. Ingestion]  --> Reads raw paragraphs from data/Innovate_AI_Hackathon_Rulebook_DataSet.docx
       │
       ▼
[2. Chunking]   --> Splits into semantic chunks with metadata (section_id, category, keywords)
       │
       ▼
[3. Embedding]  --> Generates high-dimensional vector embeddings with synonym expansion
       │
       ▼
[4. Vector DB]  --> ChromaDB persistent vector database (data/chroma_db) with Cosine Index
       │
       ▼
[5. Generator]  --> Grounded synthesis (OpenAI online mode / Offline local rulebook mode)
```

### Dual Mode Execution:
- **🌐 Online Mode:** Set `OPENAI_API_KEY=sk...` or `GEMINI_API_KEY=...` in `.env` to generate natural conversational answers using `gpt-4o-mini` with exact rulebook section citations.
- **🔌 Offline Mode:** Keep API keys commented (`# OPENAI_API_KEY=...`) in `.env` to run 100% locally and privately using the ChromaDB semantic chunk retriever.


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

## 🚀 Deploy to Vercel

The repository is pre-configured with `vercel.json`, `api/index.py`, and root `requirements.txt` for 1-click deployment on [Vercel](https://vercel.com).

### Option 1: Deploy via Vercel Web Dashboard (Recommended)
1. Push your code to GitHub.
2. Go to [vercel.com](https://vercel.com) and click **"Add New Project"** -> **"Import Git Repository"**.
3. Select this repository.
4. (Optional) In **Environment Variables**, add:
   * `ADMIN_USERNAME` = `admin`
   * `ADMIN_PASSWORD` = `your_strong_password`
   * `OPENAI_API_KEY` = `sk-...` *(optional, for online LLM mode)*
5. Click **"Deploy"**!

### Option 2: Deploy via Vercel CLI
```powershell
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

