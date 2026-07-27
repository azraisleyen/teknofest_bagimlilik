from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.devices.models import Device
from apps.yedam.models import LocationCenterMapping, YedamCenter


class Command(BaseCommand):
    help = "Create clearly labelled non-production referral demo data"

    def handle(self, *args, **options):
        center, _ = YedamCenter.objects.update_or_create(
            center_name="DEMO — NOT PRODUCTION — YEDAM",
            defaults={
                "city": "DEMO",
                "district": "DEMO",
                "address": "DEMO ADDRESS — VERIFY BEFORE USE",
                "map_place_id": "",
                "official_source_url": "https://www.yedam.org.tr/iletisim",
                "last_verified_at": timezone.now(),
                "verified_by": "DEMO — NOT PRODUCTION",
                "active": True,
            },
        )
        device, _ = Device.objects.get_or_create(
            device_name="DEMO — NOT PRODUCTION", defaults={"location_id": "demo-location"}
        )
        LocationCenterMapping.objects.update_or_create(
            location_id=device.location_id,
            defaults={
                "primary_center": center,
                "mapping_verified_at": timezone.now(),
                "active": True,
            },
        )
        self.stdout.write(f"Demo device: {device.device_id}")
