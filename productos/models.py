from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.

class Categoria(models.Model):
    """Categorías de productos (ej: Electrónica, Ropa, Hogar)"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Marca(models.Model):
    """Marcas de productos"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    logo = models.ImageField(upload_to='marcas/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Modelo principal de productos"""
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    descripcion_corta = models.CharField(max_length=300)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    
    # Precios e inventario
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0.01'))])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    sku = models.CharField(max_length=100, unique=True, help_text="Código único del producto")
    
    # Características del producto
    peso = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Peso en kg")
    dimensiones = models.CharField(max_length=100, blank=True, help_text="Alto x Ancho x Largo en cm")
    
    # Estado y visibilidad
    disponible = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False, help_text="Mostrar en página principal")
    activo = models.BooleanField(default=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['categoria', 'disponible']),
            models.Index(fields=['-fecha_creacion']),
        ]
    
    def __str__(self):
        return self.nombre
    
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


class MediaProducto(models.Model):
    """Modelo unificado para imágenes y videos de productos"""
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


# Mantengo ImagenProducto por compatibilidad, pero ahora hereda funcionalidad de MediaProducto
class ImagenProducto(models.Model):
    """Múltiples imágenes para cada producto (modelo legacy, usar MediaProducto para nuevos desarrollos)"""
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
