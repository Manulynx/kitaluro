"""
Utilidades para gestión de archivos en Cloudinary.

Evita duplicados de imágenes/videos usando:
- public_ids determinísticos basados en el ID del producto
- overwrite=True para reemplazar archivos existentes
- Limpieza explícita de recursos antiguos

Compatible con django-cloudinary-storage como DEFAULT_FILE_STORAGE.
"""

import os
import logging
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


# =============================================================================
# DETECCIÓN DE ENTORNO
# =============================================================================

def is_cloudinary_enabled():
    """Verifica si Cloudinary está configurado como storage."""
    return bool(
        os.environ.get('CLOUDINARY_URL')
        or (
            os.environ.get('CLOUDINARY_CLOUD_NAME')
            and os.environ.get('CLOUDINARY_API_KEY')
            and os.environ.get('CLOUDINARY_API_SECRET')
        )
    )


# =============================================================================
# OPTIMIZACIÓN DE IMÁGENES
# =============================================================================

def optimize_image_buffer(image_file, max_size=(1200, 1200), quality=90):
    """
    Optimiza una imagen y retorna un buffer BytesIO listo para subir.
    Convierte a JPEG, redimensiona y comprime.
    Retorna None si falla la optimización.
    """
    try:
        img = Image.open(image_file)

        # Convertir RGBA/LA/P a RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(
                img, mask=img.split()[-1] if img.mode == 'RGBA' else None
            )
            img = background

        # Redimensionar manteniendo aspecto
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        return output
    except Exception as e:
        logger.error(f"Error optimizando imagen: {e}")
        return None


# =============================================================================
# SUBIDA A CLOUDINARY CON PUBLIC_ID DETERMINÍSTICO
# =============================================================================

def _cloudinary_upload(file_obj, public_id, resource_type='image'):
    """
    Sube un archivo a Cloudinary con overwrite=True y public_id fijo.
    Retorna el public_id almacenado o None si falla.
    """
    try:
        import cloudinary.uploader

        result = cloudinary.uploader.upload(
            file_obj,
            public_id=public_id,
            overwrite=True,
            invalidate=True,
            resource_type=resource_type,
            unique_filename=False,
            use_filename=False,
        )
        return result.get('public_id', '')
    except ImportError:
        logger.warning("El paquete 'cloudinary' no está instalado.")
        return None
    except Exception as e:
        logger.error(f"Error subiendo a Cloudinary (public_id={public_id}): {e}")
        return None


def upload_product_image(image_file, producto_id):
    """
    Sube la imagen principal del producto.
    Public ID determinístico: productos/{producto_id}/main
    La imagen se optimiza antes de subir.
    """
    if not is_cloudinary_enabled():
        return None

    optimized = optimize_image_buffer(image_file)
    upload_data = optimized if optimized else image_file
    return _cloudinary_upload(upload_data, f"productos/{producto_id}/main")


def upload_product_video(video_file, producto_id):
    """
    Sube el video principal del producto.
    Public ID determinístico: productos/{producto_id}/video_main
    """
    if not is_cloudinary_enabled():
        return None

    return _cloudinary_upload(
        video_file, f"productos/{producto_id}/video_main", resource_type='video'
    )


def upload_product_file(file_obj, producto_id):
    """
    Sube la ficha técnica (PDF u otro documento).
    Public ID determinístico: productos/{producto_id}/ficha_tecnica
    """
    if not is_cloudinary_enabled():
        return None

    return _cloudinary_upload(
        file_obj, f"productos/{producto_id}/ficha_tecnica", resource_type='raw'
    )


def upload_gallery_image(image_file, producto_id, index):
    """
    Sube una imagen de galería.
    Public ID determinístico: productos/{producto_id}/galeria/{index}
    La imagen se optimiza antes de subir.
    """
    if not is_cloudinary_enabled():
        return None

    optimized = optimize_image_buffer(image_file)
    upload_data = optimized if optimized else image_file
    return _cloudinary_upload(upload_data, f"productos/{producto_id}/galeria/{index}")


def upload_gallery_video(video_file, producto_id, index):
    """
    Sube un video de galería.
    Public ID determinístico: productos/{producto_id}/videos/{index}
    """
    if not is_cloudinary_enabled():
        return None

    return _cloudinary_upload(
        video_file, f"productos/{producto_id}/videos/{index}", resource_type='video'
    )


# =============================================================================
# ELIMINACIÓN DE RECURSOS
# =============================================================================

def destroy_cloudinary_resource(public_id, resource_type='image'):
    """Elimina un recurso de Cloudinary por su public_id."""
    if not is_cloudinary_enabled() or not public_id:
        return False

    try:
        import cloudinary.uploader

        result = cloudinary.uploader.destroy(
            public_id,
            resource_type=resource_type,
            invalidate=True,
        )
        deleted = result.get('result') == 'ok'
        if deleted:
            logger.info(f"Recurso eliminado de Cloudinary: {public_id}")
        return deleted
    except ImportError:
        return False
    except Exception as e:
        logger.error(f"Error eliminando recurso de Cloudinary ({public_id}): {e}")
        return False


def get_public_id_from_field(file_field):
    """
    Extrae el public_id de Cloudinary desde un campo de archivo Django.
    Ejemplo: 'productos/galeria/abc.jpg' -> 'productos/galeria/abc'
    """
    if not file_field or not file_field.name:
        return None
    name = file_field.name
    # Remover extensión para obtener el public_id
    if '.' in name:
        name = name.rsplit('.', 1)[0]
    return name
