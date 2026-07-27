from django.core.management.base import BaseCommand

from apps.qr.services import EventService


class Command(BaseCommand):
    help = "Expire active QR events beyond the configured hard timeout"

    def handle(self, *args, **options):
        self.stdout.write(f"Expired {EventService.expire_for_device()} event(s)")
