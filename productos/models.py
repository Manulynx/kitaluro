from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from decimal import Decimal
import random
import string
import uuid
from datetime import datetime

# Create your models here.

class Proveedor(models.Model):
    """Proveedores de productos"""
    nombre = models.CharField(max_length=120, verbose_name="Nombre")
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='proveedores/', blank=True, null=True, verbose_name="Logo")
    id_unico = models.CharField(max_length=50, unique=True, verbose_name="ID Único", 
                                help_text="Identificador único del proveedor", blank=True)
    catalogo = models.FileField(upload_to='catalogos/', blank=True, null=True, verbose_name="Catálogo (PDF)")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        if not self.id_unico:
            self.id_unico = f"PROV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
    
    @property
    def productos_asociados(self):
        """Retorna todos los productos asociados a este proveedor"""
        return self.productos.filter(activo=True)
    
    def count_productos(self):
        """Cuenta los productos activos del proveedor"""
        return self.productos_asociados.count()
    count_productos.short_description = "Productos Activos"
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']


class Categoria(models.Model):
    """Categorías de productos (ej: Electrónica, Ropa, Hogar)"""
    nombre = models.CharField(max_length=120, verbose_name="Nombre", unique=True)
    descripcion = models.TextField(blank=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    @property
    def subcategorias_asociadas(self):
        """Retorna todas las subcategorías asociadas a esta categoría"""
        return self.subcategorias.all()
    
    def count_subcategorias(self):
        """Cuenta las subcategorías de la categoría"""
        return self.subcategorias_asociadas.count()
    count_subcategorias.short_description = "Subcategorías"


class Subcategoria(models.Model):
    """Subcategorías de productos"""
    nombre = models.CharField(max_length=120, verbose_name="Nombre")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="subcategorias", verbose_name="Categoría")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} ({self.categoria})"
    
    @property
    def productos_asociados(self):
        """Retorna todos los productos asociados a esta subcategoría"""
        return self.productos.filter(activo=True)
    
    def count_productos(self):
        """Cuenta los productos activos de la subcategoría"""
        return self.productos_asociados.count()
    count_productos.short_description = "Productos Activos"
    
    class Meta:
        verbose_name = "Subcategoría"
        verbose_name_plural = "Subcategorías"
        ordering = ['nombre']


class Estatus(models.Model):
    """Estatus de procedencia de productos"""
    nombre = models.CharField(max_length=120, verbose_name="Nombre")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
    
    @property
    def productos_asociados(self):
        """Retorna todos los productos asociados a este estatus"""
        return self.productos.filter(activo=True)
    
    def count_productos(self):
        """Cuenta los productos activos del estatus"""
        return self.productos_asociados.count()
    count_productos.short_description = "Productos Activos"
    
    class Meta:
        verbose_name = "Estatus de Procedencia"
        verbose_name_plural = "Estatus de Procedencia"
        ordering = ['nombre']


class Marca(models.Model):
    """Marcas de productos"""
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    logo = models.ImageField(upload_to='marcas/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Modelo principal de productos"""
    nombre = models.CharField(max_length=250, verbose_name="Nombre")
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    descripcion_corta = models.CharField(max_length=500, blank=True, verbose_name="Descripción Corta")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    
    # Relaciones
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos', verbose_name="Categoría")
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos', verbose_name="Subcategoría")
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos', verbose_name="Marca")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos', verbose_name="Proveedor")
    estatus = models.ForeignKey(Estatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos', verbose_name="Estatus de Procedencia")
    
    # Precios e inventario
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Precio")
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Precio de Oferta")
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    sku = models.CharField(max_length=100, unique=True, blank=True, verbose_name="Código SKU", help_text="Código único del producto (se genera automáticamente)")
    
    # Características del producto
    peso = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Peso en kg", verbose_name="Peso (kg)")
    dimensiones = models.CharField(max_length=100, blank=True, help_text="Alto x Ancho x Largo en cm")
    origen = models.CharField(max_length=100, blank=True, verbose_name="País de Origen")
    
    # Archivos multimedia y documentación
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen Principal")
    video = models.FileField(upload_to='productos/videos/', blank=True, null=True, verbose_name="Video del Producto")
    ficha_tecnica = models.FileField(upload_to='fichas_tecnicas/', blank=True, null=True, verbose_name="Ficha Técnica (PDF)")
    
    # Estado y visibilidad
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    destacado = models.BooleanField(default=False, help_text="Mostrar en página principal", verbose_name="Producto Destacado")
    en_oferta = models.BooleanField(default=False, verbose_name="En Oferta")
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-destacado', '-en_oferta', '-fecha_creacion']  # Destacados y ofertas primero
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['activo', 'destacado']),
            models.Index(fields=['categoria', 'disponible']),
            models.Index(fields=['proveedor', 'activo']),
            models.Index(fields=['-fecha_creacion']),
        ]
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        """Generar slug y SKU automáticamente si no existen"""
        if not self.slug:
            self.slug = slugify(self.nombre)
        if not self.sku:
            self.sku = self.generar_sku()
        super().save(*args, **kwargs)
    
    def generar_sku(self):
        """Genera un SKU único para el producto con formato PROV-CAT-YYMMDD-HHMM-UUID4"""
        if self.proveedor:
            # Usar las primeras 3 letras del proveedor
            proveedor_code = ''.join(c for c in self.proveedor.nombre if c.isalnum())[:3].upper()
        else:
            proveedor_code = 'GEN'  # General si no hay proveedor
        
        if self.categoria:
            # Usar las primeras 2 letras de la categoría
            categoria_code = ''.join(c for c in self.categoria.nombre if c.isalnum())[:2].upper()
        else:
            categoria_code = 'XX'  # Default si no hay categoría
        
        # Fecha actual en formato YYMMDD
        date_code = datetime.now().strftime('%y%m%d')
        
        # Número secuencial basado en la hora actual + últimos 4 dígitos del UUID
        time_code = datetime.now().strftime('%H%M')
        uuid_suffix = str(uuid.uuid4().hex)[-4:].upper()
        
        # Formato: PROV-CAT-YYMMDD-HHMM-UUID4
        base_sku = f"{proveedor_code}-{categoria_code}-{date_code}-{time_code}-{uuid_suffix}"
        
        # Verificar que el SKU sea único
        counter = 1
        sku = base_sku
        while Producto.objects.filter(sku=sku).exclude(pk=self.pk).exists():
            sku = f"{base_sku}-{counter:02d}"
            counter += 1
        
        return sku
    
    def get_absolute_url(self):
        """URL absoluta del producto - Importante para SEO"""
        from django.urls import reverse
        return reverse('productos:detalle', args=[self.slug])
    
    @property
    def precio_final(self):
        """Retorna el precio de oferta si existe, sino el precio regular"""
        return self.precio_oferta if self.precio_oferta else self.precio
    
    @property
    def tiene_descuento(self):
        """Indica si el producto tiene descuento"""
        return self.precio_oferta is not None and self.precio_oferta < self.precio
    
    @property
    def porcentaje_descuento(self):
        """Calcula el porcentaje de descuento"""
        if self.tiene_descuento:
            return int(((self.precio - self.precio_oferta) / self.precio) * 100)
        return 0
    
    @property
    def en_stock(self):
        """Indica si hay stock disponible"""
        return self.stock > 0
    
    @property
    def is_featured(self):
        """Retorna True si el producto está destacado"""
        return self.destacado
    
    @property
    def is_on_sale(self):
        """Retorna True si el producto está en oferta"""
        return self.en_oferta
    
    def get_status_badges(self):
        """Retorna una lista de badges de estado para mostrar en templates"""
        badges = []
        if self.en_oferta:
            badges.append({'text': 'EN OFERTA', 'class': 'bg-danger'})
        if self.destacado:
            badges.append({'text': 'DESTACADO', 'class': 'bg-warning text-dark'})
        if not self.activo:
            badges.append({'text': 'INACTIVO', 'class': 'bg-secondary'})
        return badges
    
    @classmethod
    def get_featured_products(cls):
        """Retorna productos destacados activos"""
        return cls.objects.filter(activo=True, destacado=True)
    
    @classmethod
    def get_on_sale_products(cls):
        """Retorna productos en oferta activos"""
        return cls.objects.filter(activo=True, en_oferta=True)
    
    @classmethod
    def get_featured_and_on_sale(cls):
        """Retorna productos que están destacados Y en oferta"""
        return cls.objects.filter(activo=True, destacado=True, en_oferta=True)
    
    def get_main_image(self):
        """Retorna la imagen principal del producto o la primera imagen disponible"""
        main_image = self.imagenes_galeria.filter(is_main=True).first()
        if main_image:
            return main_image.image
        first_image = self.imagenes_galeria.first()
        if first_image:
            return first_image.image
        return self.imagen  # Fallback a la imagen original del modelo
    
    @property
    def imagen_principal(self):
        """Property para acceso directo a la imagen principal desde templates"""
        main_image = self.get_main_image()
        if main_image:
            try:
                return main_image.url
            except (ValueError, AttributeError):
                return None
        return None
    
    def get_all_images(self):
        """Retorna todas las imágenes del producto ordenadas"""
        return self.imagenes_galeria.all()
    
    def get_main_video(self):
        """Retorna el primer video del producto disponible"""
        first_video = self.videos_galeria.first()
        if first_video:
            return first_video.video
        return self.video  # Fallback al video original del modelo
    
    def get_all_videos(self):
        """Retorna todos los videos del producto ordenados"""
        return self.videos_galeria.all()
    
    def has_multiple_images(self):
        """Retorna True si el producto tiene múltiples imágenes"""
        return self.imagenes_galeria.count() > 1
    
    def has_multiple_videos(self):
        """Retorna True si el producto tiene múltiples videos"""
        return self.videos_galeria.count() > 1


class ProductImage(models.Model):
    """Modelo para múltiples imágenes por producto - Galería de imágenes"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes_galeria', verbose_name="Producto")
    image = models.ImageField(upload_to='productos/galeria/', verbose_name="Imagen")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="Texto alternativo")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")
    is_main = models.BooleanField(default=False, verbose_name="Imagen principal")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagen de {self.producto.nombre} - {self.order}"

    class Meta:
        ordering = ['order', '-is_main']
        verbose_name = "Imagen de Galería"
        verbose_name_plural = "Imágenes de Galería"

    def save(self, *args, **kwargs):
        # Si es imagen principal, desmarcar otras como principales
        if self.is_main:
            ProductImage.objects.filter(producto=self.producto, is_main=True).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)


class ProductVideo(models.Model):
    """Modelo para múltiples videos por producto - Galería de videos"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='videos_galeria', verbose_name="Producto")
    video = models.FileField(upload_to='productos/videos/', verbose_name="Video")
    title = models.CharField(max_length=255, blank=True, verbose_name="Título del Video")
    description = models.TextField(blank=True, verbose_name="Descripción")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden de visualización")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video de {self.producto.nombre} - {self.title or f'Video {self.order}'}"

    class Meta:
        ordering = ['order']
        verbose_name = "Video de Galería"
        verbose_name_plural = "Videos de Galería"


class MediaProducto(models.Model):
    """Modelo unificado para imágenes y videos de productos (legacy - usar ProductImage/ProductVideo)"""
    TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='medias')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='imagen')
    
    # Para imágenes
    imagen = models.ImageField(upload_to='productos/imagenes/', blank=True, null=True)
    
    # Para videos
    video = models.FileField(upload_to='productos/videos/', blank=True, null=True, help_text="Archivo de video (MP4, WebM)")
    video_url = models.URLField(blank=True, help_text="URL de YouTube, Vimeo, etc.")
    thumbnail = models.ImageField(upload_to='productos/thumbnails/', blank=True, null=True, help_text="Miniatura del video")
    
    # Campos comunes
    alt_text = models.CharField(max_length=200, blank=True)
    titulo = models.CharField(max_length=200, blank=True)
    descripcion = models.TextField(blank=True)
    es_principal = models.BooleanField(default=False, help_text="Media principal del producto")
    orden = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Media de Producto'
        verbose_name_plural = 'Medias de Productos'
        ordering = ['orden', '-es_principal', '-fecha_creacion']
    
    def __str__(self):
        return f"{self.get_tipo_display()} de {self.producto.nombre}"
    
    def clean(self):
        """Validación personalizada"""
        from django.core.exceptions import ValidationError
        
        if self.tipo == 'imagen' and not self.imagen:
            raise ValidationError({'imagen': 'Debe proporcionar una imagen para este tipo de media.'})
        
        if self.tipo == 'video' and not self.video and not self.video_url:
            raise ValidationError({'video': 'Debe proporcionar un archivo de video o una URL.'})
    
    @property
    def es_video_externo(self):
        """Indica si el video es de una URL externa"""
        return self.tipo == 'video' and self.video_url


# Mantengo ImagenProducto por compatibilidad
class ImagenProducto(models.Model):
    """Múltiples imágenes para cada producto (modelo legacy, usar ProductImage para nuevos desarrollos)"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/')
    alt_text = models.CharField(max_length=200, blank=True)
    es_principal = models.BooleanField(default=False)
    orden = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'
        ordering = ['orden', '-es_principal']
    
    def __str__(self):
        return f"Imagen de {self.producto.nombre}"


class Valoracion(models.Model):
    """Valoraciones y reseñas de productos"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='valoraciones')
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='valoraciones_productos', null=True)
    puntuacion = models.IntegerField(validators=[MinValueValidator(1)], help_text="1-5 estrellas")
    titulo = models.CharField(max_length=200, blank=True)
    comentario = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    verificado = models.BooleanField(default=False, help_text="Compra verificada")
    
    class Meta:
        verbose_name = 'Valoración'
        verbose_name_plural = 'Valoraciones'
        ordering = ['-fecha_creacion']
        unique_together = ['producto', 'usuario']
    
    def __str__(self):
        return f"{self.puntuacion} estrellas - {self.producto.nombre}"
