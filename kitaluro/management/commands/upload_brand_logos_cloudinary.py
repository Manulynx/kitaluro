from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Uploads static brand logos from static/img/marcas to Cloudinary with deterministic public_ids. "
        "Use together with BRAND_LOGOS_USE_CLOUDINARY=true."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--folder",
            default=getattr(settings, "BRAND_LOGOS_CLOUDINARY_FOLDER", "marcas"),
            help="Cloudinary folder/prefix to use for public_ids (default: marcas)",
        )
        parser.add_argument(
            "--source",
            default=str(settings.BASE_DIR / "static" / "img" / "marcas"),
            help="Local directory containing logo images (default: <BASE_DIR>/static/img/marcas)",
        )

    def handle(self, *args, **options):
        if not getattr(settings, "CLOUDINARY_ENABLED", False):
            self.stderr.write(
                self.style.ERROR(
                    "Cloudinary is not enabled. Set CLOUDINARY_URL or CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET."
                )
            )
            return

        try:
            import cloudinary.uploader
        except Exception as exc:  # pragma: no cover
            self.stderr.write(self.style.ERROR(f"Cloudinary SDK not available: {exc}"))
            return

        source_dir = Path(options["source"]).resolve()
        if not source_dir.exists() or not source_dir.is_dir():
            self.stderr.write(self.style.ERROR(f"Source dir not found: {source_dir}"))
            return

        folder = str(options["folder"]).strip("/")
        uploaded = 0

        for path in sorted(source_dir.iterdir()):
            if not path.is_file():
                continue
            stem = path.stem
            public_id = f"{folder}/{stem}"

            try:
                result = cloudinary.uploader.upload(
                    str(path),
                    public_id=public_id,
                    overwrite=True,
                    invalidate=True,
                    resource_type="image",
                    unique_filename=False,
                    use_filename=False,
                )
                uploaded += 1
                self.stdout.write(f"OK {public_id} -> {result.get('secure_url', '')}")
            except Exception as exc:
                self.stderr.write(self.style.WARNING(f"FAIL {public_id}: {exc}"))

        self.stdout.write(self.style.SUCCESS(f"Uploaded {uploaded} logo(s)"))