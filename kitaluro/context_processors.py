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
    """Expose brand logo image URLs from static/img/marcas.

    Looks in both STATIC_ROOT and STATICFILES_DIRS for the marcas folder.
    This lets templates render a "Marcas Registradas" banner without needing
    per-view changes.
    """
    # Try STATICFILES_DIRS first (development), then STATIC_ROOT (production)
    logos_dir = None
    candidates = []
    
    for d in getattr(settings, "STATICFILES_DIRS", []):
        candidates.append(Path(d) / "img" / "marcas")
    
    static_root = Path(getattr(settings, "STATIC_ROOT", "") or "")
    if static_root:
        candidates.append(static_root / "img" / "marcas")
    
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            logos_dir = candidate
            break
    
    if not logos_dir:
        return {"brand_logos": [], "brand_logos_count": 0, "brand_logos_marquee_duration_s": 10}

    logos: list[dict[str, str]] = []
    for entry in sorted(logos_dir.iterdir()):
        if not entry.is_file():
            continue
        if entry.suffix.lower() not in _IMAGE_EXTENSIONS:
            continue

        # Build URL under STATIC_URL
        filename_stem = entry.stem
        alt = f"Logo {filename_stem}".replace("_", " ").replace("-", " ")
        logos.append(
            {
                "url": f"{settings.STATIC_URL}img/marcas/{quote(entry.name)}",
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
