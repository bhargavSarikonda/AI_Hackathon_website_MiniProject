import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
SERVER_DIR = ROOT / "server"

PROCESSES = []


def start_process(label: str, command: list[str], cwd: Path):
    print(f"Starting {label}...")
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        stdin=None,
        stdout=sys.stdout,
        stderr=sys.stderr,
        shell=False,
    )
    PROCESSES.append(process)
    return process


def stop_all():
    for process in PROCESSES:
        if process.poll() is None:
            try:
                process.terminate()
            except Exception:
                pass
    for process in PROCESSES:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                process.kill()
            except Exception:
                pass


def main():
    print("Launching Hackathon website...")

    backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
    frontend_cmd = ["node", "server.js"]

    start_process("FastAPI backend", backend_cmd, BACKEND_DIR)
    time.sleep(2)
    start_process("Frontend server", frontend_cmd, SERVER_DIR)

    time.sleep(2)
    webbrowser.open("http://localhost:3000/index.html")

    print("\nWebsite is running at: http://localhost:3000/index.html")
    print("API is running at: http://localhost:8000")
    print("Press Ctrl+C to stop the app.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        stop_all()
        print("All services stopped.")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    finally:
        stop_all()
