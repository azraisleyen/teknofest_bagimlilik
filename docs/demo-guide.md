# Demo rehberi

`apps.demo` yalnızca development'ta ve `ENABLE_DEMO_UI=True` iken yüklenir; production başlangıcı bunu reddeder. Kamera/model paneli bir yer tutucudur. Demo yalnızca `CONTENT_STARTED` ve `CONTENT_ENDED` orchestrator olaylarını simüle eder. `QrController` genel QR'ı boot ve pending sırasında korur, tam render sonrası atomik değiştirir, generation/event kontrolleriyle geç yanıtı reddeder ve hata/kapanışta genele döner. Fiziksel telefon QR testi yapılmamıştır; `docs/physical-qr-test-plan.md` durumu PENDING tutar.
