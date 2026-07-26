from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.qr.models import QrEventContext, QrToken


class Command(BaseCommand):
    help = "Purge expired QR mappings and ended contexts"

    def add_arguments(self, p):
        p.add_argument("--dry-run", action="store_true")

    def handle(self, *a, **o):
        tokens = QrToken.objects.filter(mapping_expires_at__lt=timezone.now())
        events = QrEventContext.objects.filter(
            status__in=["ENDED", "EXPIRED"], token__mapping_expires_at__lt=timezone.now()
        )
        counts = (tokens.count(), events.count())
        if not o["dry_run"]:
            tokens.delete()
        self.stdout.write(
            f"expired_tokens={counts[0]} expired_contexts={counts[1]} dry_run={o['dry_run']}"
        )
