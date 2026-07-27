from django.contrib import admin

from .models import SurveyChoice, SurveyDefinition, SurveyQuestion, SurveyResponse, SurveySession

admin.site.register(SurveyDefinition)
admin.site.register(SurveyQuestion)
admin.site.register(SurveyChoice)
admin.site.register(SurveySession)
admin.site.register(SurveyResponse)
