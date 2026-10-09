#!/bin/sh
# Serve the manuals locally with live reload: http://127.0.0.1:8000/meatpi-docs/
# Creates the Python environment on first use.
cd "$(dirname "$0")" || exit 1
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv || exit 1
  .venv/bin/python -m pip install -r requirements.txt || exit 1
fi
exec .venv/bin/python -m mkdocs serve "$@"
