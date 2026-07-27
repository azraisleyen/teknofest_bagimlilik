from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.interactions.views import InteractionView
from apps.qr.views import DisplayEventView, EventView, HealthView, LiveHealthView, ReadyHealthView
from apps.support.views import support_page
from apps.surveys.views import (
    SurveyDeclineView,
    SurveyFinishView,
    SurveyResponseView,
    SurveyStartView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("support/", support_page, name="support"),
    path("q/<str:token>", support_page, name="dynamic-support"),
    path("s/<str:installation_token>", support_page, name="device-support"),
    path("api/v1/qr/health", HealthView.as_view()),
    path("api/v1/qr/health/live", LiveHealthView.as_view()),
    path("api/v1/qr/health/ready", ReadyHealthView.as_view()),
    path("api/v1/qr/events", EventView.as_view()),
    path("api/v1/qr/display-events", DisplayEventView.as_view()),
    path("api/v1/public/interactions", InteractionView.as_view()),
    path("api/v1/public/surveys/start", SurveyStartView.as_view()),
    path("api/v1/public/surveys/<uuid:session_id>/responses", SurveyResponseView.as_view()),
    path("api/v1/public/surveys/<uuid:session_id>/complete", SurveyFinishView.as_view()),
    path("api/v1/public/surveys/<uuid:session_id>/decline", SurveyDeclineView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
]
if settings.DEBUG:
    urlpatterns += [path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"))]
if settings.ENABLE_DEMO_UI:
    urlpatterns += [path("demo/", include("apps.demo.urls"))]
