from django.urls import path

from .views import display_page, simulate_end, simulate_start

app_name = "display"

urlpatterns = [
    path("", display_page, name="screen"),
    path("api/simulate/start", simulate_start, name="simulate-start"),
    path("api/simulate/<uuid:event_id>/end", simulate_end, name="simulate-end"),
]
