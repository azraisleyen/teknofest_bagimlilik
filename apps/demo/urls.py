from django.urls import path

from .views import index, simulate

urlpatterns = [path("", index), path("simulate", simulate)]
