from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from django.conf import settings


_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif", ".avif"}


def nav_categories(request):
    """Expose active categories with their subcategories to all templates for the navbar mega menu."""
    from productos.models import Categoria
    categorias = Categoria.objects.filter(activo=True).prefetch_related('subcategorias').order_by('nombre')
    return {
        "nav_categorias": categorias,
    }


def brand_logos(request):
    """Expose brand logo image URLs from MEDIA_ROOT/marcas.

    This lets templates render a "Marcas Registradas" banner without needing
    per-view changes.
    """
    media_root = Path(getattr(settings, "MEDIA_ROOT", ""))
    if not media_root:
        return {"brand_logos": []}

    logos_dir = media_root / "marcas"
    if not logos_dir.exists() or not logos_dir.is_dir():
        return {"brand_logos": []}

    logos: list[dict[str, str]] = []
    for entry in sorted(logos_dir.iterdir()):
        if not entry.is_file():
            continue
        if entry.suffix.lower() not in _IMAGE_EXTENSIONS:
            continue

        # Build URL under MEDIA_URL; quote filename to support spaces/special chars.
        filename_stem = entry.stem
        alt = f"Logo {filename_stem}".replace("_", " ").replace("-", " ")
        logos.append(
            {
                "url": f"{settings.MEDIA_URL}marcas/{quote(entry.name)}",
                "alt": alt,
            }
        )

    # Marquee speed tuning: more logos => longer duration.
    # Tuned to feel "fast" while staying readable.
    logos_count = len(logos)
    marquee_duration_s = max(10, min(40, logos_count * 2))

    return {
        "brand_logos": logos,
        "brand_logos_count": logos_count,
        "brand_logos_marquee_duration_s": marquee_duration_s,
    }
