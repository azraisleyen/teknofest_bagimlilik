from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Idempotently create least-privilege SENTRA administration roles"

    def handle(self, *args, **options):
        roles = {
            "Center manager": [
                ("yedam", "view_yedamcenter"),
                ("yedam", "change_yedamcenter"),
                ("yedam", "view_locationcentermapping"),
                ("yedam", "change_locationcentermapping"),
            ],
            "Survey manager": [
                ("surveys", "view_surveydefinition"),
                ("surveys", "change_surveydefinition"),
            ],
            "Read-only auditor": [("audit", "view_auditlog")],
            "System administrator": [],
        }
        for name, permissions in roles.items():
            group, _ = Group.objects.get_or_create(name=name)
            group.permissions.set(
                [
                    Permission.objects.get(content_type__app_label=app, codename=code)
                    for app, code in permissions
                ]
            )
        self.stdout.write("Roles configured")
