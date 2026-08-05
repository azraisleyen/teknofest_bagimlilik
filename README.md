# SENTRA — Modüler Farkındalık, QR ve Destek Sistemi

SENTRA; modelden bağımsız tespit sinyallerini karşılayan, uygun farkındalık içeriğini oynatan, olay bazlı güvenli QR üreten, mobil YEDAM yönlendirmesi ve gönüllü mikro anket sunan Django 5.2 tabanlı modüler bir prototiptir.

Bu depo gerçek kamera/model ağırlığı içermez. Geliştirme ekranındaki işlenmiş tespit videosu yalnızca arayüz olayını simüle eder ve model başarımı kanıtı değildir. Gerçek modeller `DetectionProvider` adaptör sözleşmesi üzerinden daha sonra bağlanır.

## Hızlı başlangıç — Windows PowerShell

Python 3.12 gereklidir.

```powershell
cd C:\teknofest_bagimlilik
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements\development.txt
python manage.py migrate
python manage.py seed_demo_referral_data
python manage.py seed_sentra_content
python manage.py seed_demo_data
python manage.py generate_general_qr
python manage.py runserver 0.0.0.0:8000
```

Geliştirme ekranı: `http://127.0.0.1:8000/display/`

Mobil destek: `http://127.0.0.1:8000/support/`

Mikro anket: `http://127.0.0.1:8000/survey/`

Fiziksel telefon testi için `PUBLIC_BASE_URL`, `GENERAL_SUPPORT_URL` ve `ALLOWED_HOSTS` değerlerini bilgisayarın güncel Wi‑Fi IPv4 adresine göre düzenleyin. Telefon ve bilgisayar aynı ağda olmalıdır. Tarayıcı konumu yalnızca güvenli HTTPS bağlamında güvenilir biçimde çalışır; HTTP/LAN testinde il seçimi kullanılabilir.

## Mimari sınırlar

- QR yalnızca tahmin edilemeyen opak olay token’ı taşır; kişi sayısı, yaş tahmini, güven skoru ve kamera verisi taşımaz.
- Tokenın yalnızca SHA-256 özeti veritabanında saklanır.
- Normal içerik bitişinde olay QR’ı hemen iptal edilmez; bağlam süresi ve ekrandaki 45 saniyelik ek süre ayrı yönetilir.
- Yaş modeli yoksa, kararsızsa veya farklı yaş bantları varsa `GENERAL` içerik seçilir.
- `focus_roi` yalnızca geçiş sırasında tarayıcı belleğinde kullanılır; sunucuya ve ankete gönderilmez.
- Kullanıcı koordinatları en yakın merkez hesabı için tarayıcıda kullanılır ve sunucuya gönderilmez.
- Konum izni reddedilirse “cihaz konumuna göre” iddiası gösterilmez; il seçimi ve resmî merkez dizini sunulur.
- SENTRA, YEDAM/Yeşilay ile resmî ortaklık iddiasında bulunmaz.
- İçerik paketleri psikolog ve sağlık inceleme durumu olmadan kesin uygunluk iddiasıyla yayımlanmamalıdır.

## Üretime hazırlık

`ENABLE_DISPLAY_SIMULATOR` üretimde kapalı olmalıdır. Gerçek model adaptörü, doğrulanmış YEDAM merkez kataloğu, HTTPS, PostgreSQL/Redis, etik-KVKK kararı, psikolog/sağlık içerik onayı ve fiziksel QR testleri üretim öncesinde tamamlanmalıdır.

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
ruff check .
ruff format --check .
mypy apps clients/python
bandit -r apps clients -x '*/migrations/*'
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py check --deploy
```

Ayrıntılar için [docs/SENTRA-UPGRADE.md](docs/SENTRA-UPGRADE.md), [docs/MODULAR-ARCHITECTURE.md](docs/MODULAR-ARCHITECTURE.md) ve [docs/PRIVACY-AND-LOCATION.md](docs/PRIVACY-AND-LOCATION.md) dosyalarına bakın.
