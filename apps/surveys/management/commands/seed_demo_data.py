from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.surveys.models import SurveyChoice, SurveyDefinition, SurveyQuestion

LIKERT = [
    ("1", "Kesinlikle katılmıyorum"),
    ("2", "Katılmıyorum"),
    ("3", "Ne katılıyorum ne katılmıyorum"),
    ("4", "Katılıyorum"),
    ("5", "Kesinlikle katılıyorum"),
    ("98", "Yanıtlamak istemiyorum"),
]
SEEN = {"EXPOSURE_LEVEL": ["FULL", "MOST", "PARTIAL"]}
SHORT = {"EXPOSURE_LEVEL": ["NOT_SEEN", "UNSURE", "PREFER_NOT"]}


QUESTIONS = [
    (
        "EXPOSURE_LEVEL",
        "İçeriği görme kontrolü",
        "SINGLE_CHOICE",
        "QR kodu okutmadan hemen önce ekrandaki animasyonu ne ölçüde izlediniz?",
        [
            ("FULL", "Tamamını izledim"),
            ("MOST", "Tamamını veya büyük bölümünü izledim"),
            ("PARTIAL", "Yalnızca bir kısmını izledim"),
            ("NOT_SEEN", "İçeriği görmedim"),
            ("UNSURE", "Emin değilim veya hatırlamıyorum"),
            ("PREFER_NOT", "Yanıtlamak istemiyorum"),
        ],
        {},
        False,
    ),
    (
        "SLOGAN_EXPOSURE",
        "İçeriği görme kontrolü",
        "SINGLE_CHOICE",
        "Animasyonun sonundaki kapanış sloganını gördünüz mü?",
        [
            ("YES", "Evet"),
            ("NO", "Hayır"),
            ("UNSURE", "Emin değilim veya hatırlamıyorum"),
            ("PREFER_NOT", "Yanıtlamak istemiyorum"),
        ],
        SEEN,
        False,
    ),
    (
        "A1_MESSAGE_CLARITY",
        "Anlaşılabilirlik",
        "LIKERT",
        "Animasyonun ana mesajını kolayca anladım.",
        LIKERT,
        SEEN,
        False,
    ),
    (
        "A2_CONTENT_COHERENCE",
        "Anlaşılabilirlik",
        "LIKERT",
        "Görsel anlatım, altyazı ve kapanış sloganı ana mesajı tutarlı biçimde aktardı.",
        LIKERT,
        {**SEEN, "SLOGAN_EXPOSURE": ["YES"]},
        False,
    ),
    (
        "B1_REFLECTION",
        "Algılanan etki",
        "LIKERT",
        "İçerik, sigara ve tütün kullanımının etkileri üzerine düşünmemi sağladı.",
        LIKERT,
        SEEN,
        False,
    ),
    (
        "B2_SUPPORT_CONSIDERATION",
        "Algılanan etki",
        "LIKERT",
        "İçerik, gerektiğinde kendim veya bir yakınım için destek seçeneğini değerlendirmemi sağladı.",
        LIKERT[:-1] + [("97", "Bu ifade benim durumum için geçerli değil")] + LIKERT[-1:],
        SEEN,
        True,
    ),
    (
        "C1_YEDAM_COMPREHENSION",
        "YEDAM desteği",
        "SINGLE_CHOICE",
        "YEDAM 115 hizmetini aşağıdaki seçeneklerden hangisi en doğru açıklar?",
        [
            (
                "CORRECT",
                "Bağımlılıklar hakkında bilgi, danışmanlık, psikolojik-sosyal destek ve yönlendirme sunan bir hizmettir",
            ),
            ("REPORT", "Sigara kullanan kişileri yönetime bildiren bir ihbar hattıdır"),
            ("EMERGENCY", "Yalnızca acil tıbbi müdahale sağlayan bir servistir"),
            ("APPOINTMENT", "Yalnızca otomatik randevu oluşturan bir sistemdir"),
            ("UNSURE", "Emin değilim"),
            ("PREFER_NOT", "Yanıtlamak istemiyorum"),
        ],
        SEEN,
        False,
    ),
    (
        "C2_SUPPORT_NAVIGATION",
        "YEDAM desteği",
        "LIKERT",
        "Gerektiğinde 115’e veya YEDAM merkezlerine nasıl ulaşabileceğimi anladım.",
        LIKERT,
        SEEN,
        False,
    ),
    (
        "D1_JUDGMENT",
        "Psikolojik güvenlik",
        "LIKERT",
        "İçeriğin, sigara veya tütün kullanan kişilere yönelik yargılayıcı bir yaklaşım içerdiğini düşündüm.",
        LIKERT,
        SEEN,
        False,
    ),
    (
        "D2_PRESSURE",
        "Psikolojik güvenlik",
        "LIKERT",
        "İçeriğin karar özgürlüğüm üzerinde baskı oluşturduğunu hissettim.",
        LIKERT,
        SEEN,
        False,
    ),
    (
        "D3_ANGER",
        "Psikolojik güvenlik",
        "LIKERT",
        "İçeriğin bende öfke oluşturduğunu hissettim.",
        LIKERT,
        SEEN,
        False,
    ),
    (
        "E1_PRIVACY_CLARITY",
        "Mahremiyet ve kabul",
        "LIKERT",
        "Anket ve sistemin veri kullanımı hakkında verilen açıklamalar açık ve anlaşılırdı.",
        LIKERT,
        SEEN,
        False,
    ),
    (
        "E2_PRIVACY_TRUST",
        "Mahremiyet ve kabul",
        "LIKERT",
        "Verilen açıklamalar doğrultusunda sistemin mahremiyet yaklaşımını güven verici buluyorum.",
        LIKERT,
        SEEN,
        False,
    ),
    (
        "E3_CAMPUS_ACCEPTABILITY",
        "Mahremiyet ve kabul",
        "LIKERT",
        "Belirtilen mahremiyet önlemleri uygulandığında sistemin üniversite ortamında kullanılmasını kabul edilebilir buluyorum.",
        LIKERT,
        SEEN,
        False,
    ),
    (
        "U1_SUPPORT_NAVIGATION",
        "Kısa destek değerlendirmesi",
        "LIKERT",
        "Gerektiğinde 115’e veya YEDAM merkezlerine nasıl ulaşabileceğimi anladım.",
        LIKERT,
        SHORT,
        False,
    ),
    (
        "U2_PRIVACY_CLARITY",
        "Kısa destek değerlendirmesi",
        "LIKERT",
        "Anket ve sistemin veri kullanımı hakkında verilen açıklamalar açık ve anlaşılırdı.",
        LIKERT,
        SHORT,
        False,
    ),
    (
        "U3_PRIVACY_TRUST",
        "Kısa destek değerlendirmesi",
        "LIKERT",
        "Verilen açıklamalar doğrultusunda sistemin mahremiyet yaklaşımını güven verici buluyorum.",
        LIKERT,
        SHORT,
        False,
    ),
    (
        "TOBACCO_RELATION",
        "İsteğe bağlı bağlam",
        "SINGLE_CHOICE",
        "Sigara veya diğer tütün ürünleriyle ilişkinizi aşağıdaki seçeneklerden hangisi en iyi açıklıyor?",
        [
            ("CURRENT", "Hâlen kullanıyorum; her gün veya ara sıra kullanabilirim"),
            ("FORMER", "Daha önce kullanıyordum, artık kullanmıyorum"),
            ("RELATIVE", "Kendim kullanmıyorum ancak kullanan bir yakınım var"),
            ("NONUSER", "Kullanmadım veya kullanmıyorum"),
            ("PREFER_NOT", "Yanıtlamak istemiyorum"),
        ],
        {},
        False,
    ),
    (
        "OPEN_FEEDBACK",
        "İsteğe bağlı geri bildirim",
        "TEXT",
        "İçerik, slogan, destek sayfası veya YEDAM yönlendirmesi hakkında paylaşmak istediğiniz başka bir görüş var mı?",
        [],
        {},
        False,
    ),
]


class Command(BaseCommand):
    help = "Seed the versioned SENTRA field micro-survey 1.1 draft."

    def handle(self, *args, **options):
        SurveyDefinition.objects.update(active=False)
        survey, _ = SurveyDefinition.objects.update_or_create(
            name="SENTRA Üniversite Saha Mikro Anketi",
            version=11,
            defaults={
                "status": "PUBLISHED",
                "active": True,
                "published_at": timezone.now(),
                "intro_text": "Gönüllü, anonim ve yaklaşık 1–2 dakikalık içerik değerlendirmesi.",
            },
        )
        keep = []
        for position, item in enumerate(QUESTIONS, 1):
            code, section, kind, text, choices, condition, allow_na = item
            question, _ = SurveyQuestion.objects.update_or_create(
                survey=survey,
                code=code,
                defaults={
                    "position": position,
                    "section": section,
                    "question_type": kind,
                    "text": text,
                    "help_text": (
                        "Lütfen ad, telefon, e-posta, sağlık kaydı veya tanımlayıcı bilgi yazmayın. En fazla 300 karakter."
                        if code == "OPEN_FEEDBACK"
                        else ""
                    ),
                    "required": code == "EXPOSURE_LEVEL",
                    "max_length": 300 if kind == "TEXT" else None,
                    "metric_key": code.lower(),
                    "reverse_scored": code.startswith("D"),
                    "allow_not_applicable": allow_na,
                    "display_condition": condition,
                },
            )
            keep.append(question.question_id)
            SurveyChoice.objects.filter(question=question).delete()
            SurveyChoice.objects.bulk_create(
                [
                    SurveyChoice(question=question, position=index, value=value, label=label)
                    for index, (value, label) in enumerate(choices, 1)
                ]
            )
        survey.questions.exclude(question_id__in=keep).delete()
        self.stdout.write(self.style.SUCCESS("SENTRA micro survey 1.1 draft ready"))
