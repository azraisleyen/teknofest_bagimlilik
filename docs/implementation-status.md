# Uygulama durumu

## Uygulanan

- Global, cihaz-token ve dinamik-event destek rotaları; token hash saklama ve rotasyon/iptal komutu.
- Güncellik kontrollü birincil/yedek merkez seçimi ve sunucuda güvenli Google Maps directions URL üretimi.
- Device DRF principal uyumu, location eşleşmesi, clock-skew ve olay sırası doğrulaması, hard-timeout expiry komutu.
- Display idempotency; gerçek database/cache readiness ve ayrı liveness.
- Onam/sahiplik bağlı anket oturumu, tip/choice/required doğrulaması, immutable context snapshot alanları.
- Immutable admin audit görünümü, kontrollü YEDAM admin'i ve idempotent rol komutu.

## Açık doğrulamalar

Gerçek YEDAM veri seti yetkili tarafından import edilmemiştir. Anket uzman/etik/hukuk onayı bekler. Fiziksel QR, saha erişilebilirliği, SmokeVision entegrasyonu ve gerçek PostgreSQL/Redis yük testi yapılmamıştır. Saklama günleri yapılandırılabilir politika olup hukuk tarafından nihai ilan edilmemiştir.
