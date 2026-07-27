from django.core.management.base import BaseCommand

from apps.surveys.models import SurveyChoice, SurveyDefinition, SurveyQuestion


class Command(BaseCommand):
    help = "Seed clearly labelled non-production demo survey data"

    def handle(self, *a, **o):
        survey, _ = SurveyDefinition.objects.get_or_create(
            name="DEMO — DO NOT USE IN PRODUCTION",
            version=1,
            defaults={
                "status": "PUBLISHED",
                "active": True,
                "intro_text": "DRAFT — EXPERT REVIEW REQUIRED",
            },
        )
        q, _ = SurveyQuestion.objects.get_or_create(
            survey=survey,
            position=1,
            defaults={
                "question_type": "LIKERT",
                "text": "Mesajı anlaşılır buldunuz mu?",
                "required": False,
            },
        )
        [
            SurveyChoice.objects.get_or_create(question=q, position=i, label=str(i), value=str(i))
            for i in range(1, 6)
        ]
        self.stdout.write(self.style.SUCCESS("Demo data ready"))
