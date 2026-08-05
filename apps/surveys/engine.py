from .branching import condition_matches
from .models import SurveyDefinition, SurveyQuestion


class SurveyEngine:
    @staticmethod
    def active_definition() -> SurveyDefinition | None:
        return (
            SurveyDefinition.objects.filter(active=True, status="PUBLISHED")
            .order_by("-version")
            .first()
        )

    @staticmethod
    def visible_questions(survey: SurveyDefinition, answers: dict) -> list[SurveyQuestion]:
        return [
            question
            for question in survey.questions.all()
            if condition_matches(question.display_condition, answers)
        ]
