# SENTRA Modular QR Support, Referral, and Research System

Independent Django 5.2 modular monolith for authenticated content lifecycle events, safe general/dynamic QR links, YEDAM referrals, an optional privacy-preserving survey, and a removable simulator. It performs **no camera, AI, person, age, or smoking detection**.

## Quick start

Python 3.12 is required. Copy `.env.example` to `.env`, replace development placeholders, and ensure `PUBLIC_BASE_URL` is reachable by the intended scanner.

**Windows PowerShell**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements/development.txt
py manage.py migrate
py manage.py generate_general_qr
py manage.py seed_demo_data
py manage.py runserver
```

**Linux/macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements/development.txt
python manage.py migrate
python manage.py generate_general_qr
python manage.py seed_demo_data
python manage.py runserver
```

Create a device in `/admin/`, then run `python manage.py create_device_credential DEVICE_UUID`; its secret is shown exactly once. Set `ENABLE_DEMO_UI=True` only in development and open `/demo/`. General mobile support is `/support/`; dynamic links use `/q/{opaque-token}`. Development OpenAPI and Swagger are `/api/schema/` and `/api/docs/`; admin is `/admin/`.

## Commands and quality

```bash
python manage.py makemigrations --check --dry-run
python manage.py check
python manage.py spectacular --file openapi.yaml --validate
pytest --cov=apps --cov=clients
ruff check . && ruff format --check .
mypy apps clients/python
bandit -r apps clients -x '*/migrations/*'
pip-audit -r requirements/production.txt
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py check --deploy
python manage.py purge_expired_qr_data --dry-run
python manage.py check_yedam_verification
python manage.py export_aggregate_metrics
```

## Docker and operations

Set production values in `.env`, then run `docker compose build && docker compose up -d db app`. Run migrations once as a release task: `docker compose run --rm app python manage.py migrate`; do not run migrations concurrently on every replica. Back up PostgreSQL with encrypted `pg_dump`, test restores, retain the previous image for rollback, and serve `/static/qr/general.svg` plus a static support fallback from highly available infrastructure. Redis is enabled with `docker compose --profile redis up`.

A phone cannot reach the computer's `localhost`. For physical testing bind to `0.0.0.0`, use a trusted LAN address in `PUBLIC_BASE_URL`, and restrict the firewall. Optional tunnels must be configured manually; no tunnel or credentials are created here.

See `docs/` for architecture, contracts, state machine, privacy, security, deployment, operations, integration, data definitions, and the pending physical QR test plan. Future SmokeVision integration uses only the versioned server-to-server events and framework-independent clients; it must never send camera/person/model data.

## Python packaging and CI

`pyproject.toml` is the authoritative application dependency and build metadata source. The
requirements files select the base editable application install and add only environment-specific
tooling. Setuptools discovery is deliberately restricted to the Django `apps` and `config`
packages plus the framework-independent `sentra_qr_client`; repository directories such as
`contracts`, `docs`, `static`, and `templates` are not accidentally interpreted as Python packages.
Runtime JSON schemas are copied into `apps.qr.schemas.v1` and included as wheel package data, while
the root `contracts/v1` copy remains the public integration artifact.

CI performs three independent jobs:

1. **Quality and tests** installs the complete development environment, runs `pip check`, Ruff,
   mypy, coverage, migration consistency, Django checks, and two OpenAPI validators.
2. **Package** builds both an isolated sdist and wheel, validates metadata, installs the wheel and its locked dependencies
   into a fresh virtual environment, imports every public package, and checks
   that runtime schemas are present.
3. **Security** runs Bandit, audits the locked production dependency graph, and executes Django's
   production deployment assessment with non-secret CI-only placeholders.

To reproduce the packaging gate locally:

```bash
python -m pip install --upgrade pip
python -m pip install build==1.3.0 twine==6.1.0
rm -rf build dist *.egg-info
python -m build
python -m twine check --strict dist/*
```
