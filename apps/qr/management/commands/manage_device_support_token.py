from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.devices.models import Device
from apps.qr.models import DeviceSupportToken
from apps.qr.tokens import TokenService


class Command(BaseCommand):
    help = "Create, rotate, or revoke an opaque device support token"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["create", "rotate", "revoke"])
        parser.add_argument("device_id")

    def handle(self, *args, **options):
        try:
            device = Device.objects.get(pk=options["device_id"])
        except Device.DoesNotExist as exc:
            raise CommandError("Device not found") from exc
        active = DeviceSupportToken.objects.filter(device=device, status="ACTIVE")
        if options["action"] in {"rotate", "revoke"}:
            active.update(status="REVOKED", revoked_at=timezone.now())
        if options["action"] == "revoke":
            self.stdout.write("Revoked")
            return
        raw = TokenService.create_random()
        DeviceSupportToken.objects.create(device=device, token_hash=TokenService.lookup_hash(raw))
        self.stdout.write("Token is shown once; store it securely:")
        self.stdout.write(raw)
