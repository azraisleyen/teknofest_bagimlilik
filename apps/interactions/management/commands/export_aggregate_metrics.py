import json

from django.core.management.base import BaseCommand
from django.db.models import Count

from apps.interactions.models import QrInteraction


class Command(BaseCommand):
    help = "Export privacy-preserving aggregate interaction counts"

    def handle(self, *a, **o):
        self.stdout.write(
            json.dumps(
                list(
                    QrInteraction.objects.values("interaction_type").annotate(
                        count=Count("interaction_id")
                    )
                ),
                default=str,
            )
        )
