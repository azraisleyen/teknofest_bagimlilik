#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"; python -m pytest; ruff check .; ruff format --check .; mypy apps clients/python
