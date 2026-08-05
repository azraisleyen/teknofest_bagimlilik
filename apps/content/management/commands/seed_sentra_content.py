from django.core.management.base import BaseCommand

from apps.content.models import ContentPackage


class Command(BaseCommand):
    help = "Create or update the review-pending SENTRA demo content catalog."

    def handle(self, *args, **options):
        package, _ = ContentPackage.objects.update_or_create(
            content_id="heart-impact-young-adult",
            version=1,
            defaults={
                "title": "Kalp ve Dolaşım Üzerindeki Etkiler",
                "age_band": ContentPackage.AgeBand.YOUNG_ADULT,
                "video_asset": "content/young_adult/heart_impact_v1.mp4",
                "poster_asset": "content/young_adult/heart_impact_v1.jpg",
                "caption_asset": "content/young_adult/heart_impact_v1.tr.vtt",
                "duration_ms": 10005,
                "language": "tr",
                "slogan_in_video": True,
                "psychologist_review_status": ContentPackage.ReviewStatus.PENDING,
                "health_review_status": ContentPackage.ReviewStatus.PENDING,
                "active": True,
                "priority": 10,
                "file_hash": "95dd30b683cb31e7f07e5f6c8a55805a1255ee47a44e00580382ba30b9fd6046",
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Content ready: {package.content_id}"))
