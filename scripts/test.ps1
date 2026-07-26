$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
py -m pytest
ruff check .
ruff format --check .
mypy apps clients/python
