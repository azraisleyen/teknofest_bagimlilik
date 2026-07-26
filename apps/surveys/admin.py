from django.contrib import admin

from .models import *  # noqa: F403

for model in list(locals().values()):
    if isinstance(model, type) and hasattr(model, "_meta"):
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
