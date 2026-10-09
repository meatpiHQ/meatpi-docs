@echo off
rem Serve the manuals locally with live reload: http://127.0.0.1:8000/meatpi-docs/
rem Creates the Python environment on first use.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv || exit /b 1
  .venv\Scripts\python -m pip install -r requirements.txt || exit /b 1
)
.venv\Scripts\python -m mkdocs serve %*
