import pytest
from django.core.management import call_command
from django.urls import reverse

from apps.surveys.branching import condition_matches
from apps.surveys.models import SurveyDefinition

pytestmark = pytest.mark.django_db


def test_code_based_branching_is_deterministic():
    condition = {"EXPOSURE_LEVEL": ["FULL", "PARTIAL"], "SLOGAN_EXPOSURE": ["YES"]}
    assert condition_matches(condition, {"EXPOSURE_LEVEL": "FULL", "SLOGAN_EXPOSURE": "YES"})
    assert not condition_matches(
        condition, {"EXPOSURE_LEVEL": "NOT_SEEN", "SLOGAN_EXPOSURE": "YES"}
    )


def test_seeded_micro_survey_has_versioned_codes_and_no_age_group():
    call_command("seed_demo_data")
    survey = SurveyDefinition.objects.get(active=True)
    codes = list(survey.questions.values_list("code", flat=True))
    assert survey.version == 11
    assert "AGE_GROUP" not in codes
    assert {"EXPOSURE_LEVEL", "U3_PRIVACY_TRUST", "E3_CAMPUS_ACCEPTABILITY"} <= set(codes)
    assert survey.questions.get(code="OPEN_FEEDBACK").max_length == 300


def test_survey_page_is_html_not_browsable_api(client):
    response = client.get(reverse("survey-flow"))
    assert response.status_code == 200
    assert b"Django REST framework" not in response.content
    assert b"SENTRA" in response.content


def test_survey_session_requires_adult_attestation_and_consent(client):
    call_command("seed_demo_data")
    client.get(reverse("survey-flow"))
    response = client.post(
        "/api/v1/public/surveys/start",
        {"consent": "yes", "age_eligible": False},
        content_type="application/json",
    )
    assert response.status_code == 400
