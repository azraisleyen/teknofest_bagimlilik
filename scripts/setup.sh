#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
python3 -m venv .venv; .venv/bin/python -m pip install --upgrade pip; .venv/bin/python -m pip install -r requirements/development.txt; .venv/bin/python manage.py migrate; .venv/bin/python manage.py generate_general_qr
