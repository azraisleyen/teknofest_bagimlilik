from django.core.management.base import BaseCommand, CommandError

from apps.devices.models import Device


class Command(BaseCommand):
    help = "Create or rotate a device credential; the secret is displayed once"

    def add_arguments(self, p):
        p.add_argument("device_id")

    def handle(self, *a, **o):
        try:
            device = Device.objects.get(device_id=o["device_id"])
        except Device.DoesNotExist as exc:
            raise CommandError("Device not found") from exc
        self.stdout.write("Store this credential securely; it will not be shown again:")
        self.stdout.write(device.issue_credential())
