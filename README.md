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

## Uçtan uca destek bağlamları

Sistem GPS istemez ve kamera/model verisi işlemez. `/support/` global fallback, `/s/<opak-token>` sabit cihaz kurulumu, `/q/<opak-token>` ise süreli orchestrator olayı bağlamıdır. Cihaz token'ları `manage_device_support_token create|rotate|revoke DEVICE_UUID` ile yönetilir; yalnızca SHA-256 özeti saklanır. Merkez yönlendirmesi doğrulanmış cihaz konum eşlemesinden üretilir ve başlangıç konumu Google Maps URL'sine eklenmez.

Windows geliştirmede Python 3.12 doğrulandıktan sonra `python` komutu kullanılabilir. `.env.example` dosyasını `.env` olarak kopyalayın; gerçek süreç environment değerleri dosyadakilerden önceliklidir. Telefon testi için `PUBLIC_BASE_URL=http://LAN_IP:8000`, `ALLOWED_HOSTS=LAN_IP,localhost`, sınırlı yerel firewall kuralı ve `python manage.py runserver 0.0.0.0:8000` gerekir. Demo sırası: `migrate`, `seed_demo_referral_data`, `seed_demo_data`, `generate_general_qr`, `ENABLE_DEMO_UI=True` ile sunucuyu açma. Demo merkezi üretim verisi değildir.
