from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.yedam.models import YedamCenter


class Command(BaseCommand):
    help = "Fail when active YEDAM center verification is stale"

    def handle(self, *a, **o):
        count = YedamCenter.objects.filter(
            active=True,
            last_verified_at__lt=timezone.now() - timedelta(days=settings.YEDAM_STALE_DAYS),
        ).count()
        if count:
            raise CommandError(f"stale_centers={count}")
        self.stdout.write(self.style.SUCCESS("All active center records are current"))
