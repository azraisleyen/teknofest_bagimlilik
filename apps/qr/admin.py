from django.contrib import admin

from .models import QrDisplaySession, QrEventContext, QrToken

admin.site.register([QrDisplaySession, QrEventContext, QrToken])
