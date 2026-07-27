from django.contrib import admin

from .models import SurveyChoice, SurveyDefinition, SurveyQuestion, SurveyResponse, SurveySession

admin.site.register([SurveyChoice, SurveyDefinition, SurveyQuestion, SurveyResponse, SurveySession])
