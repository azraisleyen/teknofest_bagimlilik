# SENTRA 1.1 yükseltme ve inceleme rehberi

## Mevcut depoya uygulama

1. Çalışma ağacının temiz olduğundan emin olun: `git status`.
2. `main` dalını güncelleyin: `git switch main` ve `git pull origin main`.
3. Yeni dal oluşturun: `git switch -c feat/sentra-modular-display-and-qr`.
4. Bu paketteki dosyaları depo köküne kopyalayın; `.git`, `.env` ve yerel veritabanını kopyalamayın.
5. Sanal ortamı etkinleştirip bağımlılıkları kurun.
6. `python manage.py migrate` çalıştırın.
7. Demo kataloglarını sırayla oluşturun: `seed_demo_referral_data`, `seed_sentra_content`, `seed_demo_data`, `generate_general_qr`.
8. `python manage.py check` ve `pytest` ile doğrulayın.
9. `/display/`, `/support/` ve `/survey/` akışlarını masaüstü ve telefonda inceleyin.

## Geri alma

Kod değişiklikleri ayrı özellik dalında tutulmalıdır. Yayına alınmamış denemeyi geri almak için dala geçmeden `main` üzerinde işlem yapmayın. Migration geri alma üretim verisi içerebileceğinden doğrudan uygulanmamalı; önce yedek ve kontrollü ortamda test edilmelidir.
