from django.contrib import admin

from .models import SurveyChoice, SurveyDefinition, SurveyQuestion, SurveyResponse, SurveySession


class SurveyChoiceInline(admin.TabularInline):
    model = SurveyChoice
    extra = 0
    ordering = ("position",)


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ("code", "survey", "section", "position", "question_type", "required")
    list_filter = ("survey", "section", "question_type", "required")
    search_fields = ("code", "text", "metric_key")
    ordering = ("survey", "position")
    inlines = [SurveyChoiceInline]


@admin.register(SurveyDefinition)
class SurveyDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "status", "active", "published_at")
    list_filter = ("status", "active")
    search_fields = ("name",)


@admin.register(SurveySession)
class SurveySessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "survey", "status", "context_mode", "started_at")
    list_filter = ("status", "context_mode", "survey")
    readonly_fields = [field.name for field in SurveySession._meta.fields]


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "created_at")
    list_filter = ("question__survey", "question__section")
    readonly_fields = [field.name for field in SurveyResponse._meta.fields]
