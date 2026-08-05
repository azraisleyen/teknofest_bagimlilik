import uuid

from django.core.validators import MinValueValidator
from django.db import models


class ContentPackage(models.Model):
    class AgeBand(models.TextChoices):
        YOUNG_ADULT = "YOUNG_ADULT", "18–34"
        MIDDLE_AGE = "MIDDLE_AGE", "35–54"
        OLDER_ADULT = "OLDER_ADULT", "55+"
        GENERAL = "GENERAL", "Genel"

    class ReviewStatus(models.TextChoices):
        PENDING = "PENDING", "İnceleme bekliyor"
        APPROVED = "APPROVED", "Onaylandı"
        REJECTED = "REJECTED", "Uygun bulunmadı"

    package_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_id = models.SlugField(max_length=160)
    version = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=180)
    age_band = models.CharField(max_length=20, choices=AgeBand)
    video_asset = models.CharField(max_length=320)
    poster_asset = models.CharField(max_length=320, blank=True)
    caption_asset = models.CharField(max_length=320, blank=True)
    duration_ms = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    language = models.CharField(max_length=12, default="tr")
    slogan_in_video = models.BooleanField(default=True)
    psychologist_review_status = models.CharField(
        max_length=12, choices=ReviewStatus, default=ReviewStatus.PENDING
    )
    health_review_status = models.CharField(
        max_length=12, choices=ReviewStatus, default=ReviewStatus.PENDING
    )
    active = models.BooleanField(default=False)
    priority = models.PositiveSmallIntegerField(default=100)
    file_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "content_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["content_id", "version"], name="unique_content_package_version"
            )
        ]

    def __str__(self):
        return f"{self.title} · v{self.version}"
