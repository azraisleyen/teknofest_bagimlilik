# SENTRA 1.1.0 — inceleme paketi

Bu paket `main` dalındaki `bca9aa2cb7b181d33635e1f75ea3ebbe1087a231` sürümü temel alınarak `feat/sentra-modular-display-and-qr` çalışma dalında hazırlanmıştır.

## Başlıca değişiklikler

- SENTRA markalı, 1920×1080 odaklı modüler büyük ekran deneyimi
- Tespit panelinden içerik paneline gizlilik kontrollü ROI geçişi
- Demo, WebSocket, HTTP, yerel Python köprüsü, manuel ve çoklu model adaptörleri
- Sürümlü yaş bandı içerik kataloğu ve güvenli `GENERAL` geri dönüşü
- Animasyon bitişinden bağımsız, 45 saniye ekran ek süreli olay QR yaşam döngüsü
- Mobil öncelikli YEDAM destek ekranı ve tarayıcı içinde en yakın merkez hesabı
- Konum reddinde il seçimi ve resmî dizin geri dönüşü
- `sentra_field_micro_survey_1.1-draft` kod tabanlı dallanma ve 300 karakter geri bildirim
- İçerik, YEDAM, anket, mahremiyet ve yükseltme belgeleri

## Doğrulama sonucu

- 38 Pytest testi başarılı
- Ruff ve Ruff format başarılı
- mypy başarılı
- Bandit başarılı
- Django sistem ve migration kontrolleri başarılı
- OpenAPI şema doğrulaması başarılı
- Üretim `check --deploy` başarılı
- `pip-audit` bilinen güvenlik açığı bildirmedi
- Wheel ve kaynak dağıtım paketi `twine check` doğrulamasını geçti

Tarayıcı tabanlı fiziksel QR, gerçek kamera/model ve HTTPS konum testleri hedef donanım ile ayrıca yapılmalıdır.
