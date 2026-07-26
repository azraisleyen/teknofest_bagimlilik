import json

from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from apps.yedam.models import YedamCenter
from apps.yedam.services import safe_map_url


class Command(BaseCommand):
    help = "Import externally verified YEDAM centers from JSON"

    def add_arguments(self, p):
        p.add_argument("file")
        p.add_argument("--dry-run", action="store_true")

    def handle(self, *a, **o):
        try:
            records = json.load(open(o["file"], encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError("Invalid JSON input") from exc
        for row in records:
            required = {
                "center_name",
                "city",
                "district",
                "address",
                "official_source_url",
                "last_verified_at",
                "verified_by",
            }
            if not required <= row.keys() or (
                row.get("map_url") and not safe_map_url(row["map_url"])
            ):
                raise CommandError("Invalid center record")
            if not o["dry_run"]:
                YedamCenter.objects.update_or_create(
                    center_id=row.get("center_id"),
                    defaults={**row, "last_verified_at": parse_datetime(row["last_verified_at"])},
                )
        self.stdout.write(self.style.SUCCESS(f"validated={len(records)} dry_run={o['dry_run']}"))
