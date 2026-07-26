from pathlib import Path

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate reproducible general-support SVG and PNG QR assets"

    def handle(self, *a, **o):
        target = Path(settings.BASE_DIR) / "static/qr"
        target.mkdir(parents=True, exist_ok=True)
        level = (
            qrcode.constants.ERROR_CORRECT_Q
            if settings.QR_ERROR_CORRECTION == "Q"
            else qrcode.constants.ERROR_CORRECT_M
        )
        qr = qrcode.QRCode(error_correction=level, border=4, box_size=10)
        qr.add_data(settings.GENERAL_SUPPORT_URL)
        qr.make(fit=True)
        qr.make_image(image_factory=qrcode.image.svg.SvgPathImage).save(target / "general.svg")
        qr.make_image(fill_color="black", back_color="white").save(target / "general.png")
        self.stdout.write(self.style.SUCCESS("General QR assets generated"))
