from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Marca, Producto, MediaProducto, ImagenProducto, Valoracion

# Register your models here.

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['activo']


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']


class MediaProductoInline(admin.TabularInline):
    model = MediaProducto
    extra = 1
    fields = ['tipo', 'imagen', 'video', 'video_url', 'thumbnail', 'titulo', 'es_principal', 'orden', 'activo']
    readonly_fields = []


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    fields = ['imagen', 'alt_text', 'es_principal', 'orden']


class ValoracionInline(admin.TabularInline):
    model = Valoracion
    extra = 0
    fields = ['usuario', 'puntuacion', 'titulo', 'comentario', 'verificado']
    readonly_fields = ['fecha_creacion']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'sku', 'categoria', 'marca', 'precio_display', 'stock', 'disponible', 'destacado', 'fecha_creacion']
    list_filter = ['categoria', 'marca', 'disponible', 'destacado', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'sku']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['disponible', 'destacado', 'stock']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'slug', 'sku', 'descripcion_corta', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('categoria', 'marca')
        }),
        ('Precios e Inventario', {
            'fields': ('precio', 'precio_oferta', 'stock')
        }),
        ('Características', {
            'fields': ('peso', 'dimensiones'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('disponible', 'destacado', 'activo')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MediaProductoInline, ImagenProductoInline, ValoracionInline]
    
    def precio_display(self, obj):
        if obj.precio_oferta:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">${}</span> <strong style="color: #28a745;">${}</strong>',
                obj.precio, obj.precio_oferta
            )
        return f'${obj.precio}'
    precio_display.short_description = 'Precio'


@admin.register(MediaProducto)
class MediaProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'titulo', 'es_principal', 'orden', 'activo', 'fecha_creacion']
    list_filter = ['tipo', 'es_principal', 'activo', 'fecha_creacion']
    search_fields = ['producto__nombre', 'titulo', 'descripcion']
    list_editable = ['es_principal', 'orden', 'activo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('producto', 'tipo', 'titulo', 'descripcion')
        }),
        ('Imagen', {
            'fields': ('imagen', 'alt_text'),
            'classes': ('collapse',)
        }),
        ('Video', {
            'fields': ('video', 'video_url', 'thumbnail'),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('es_principal', 'orden', 'activo')
        }),
    )


@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'es_principal', 'orden', 'fecha_creacion']
    list_filter = ['es_principal', 'fecha_creacion']
    search_fields = ['producto__nombre', 'alt_text']
    list_editable = ['es_principal', 'orden']


@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ['producto', 'usuario', 'puntuacion', 'titulo', 'verificado', 'fecha_creacion']
    list_filter = ['puntuacion', 'verificado', 'fecha_creacion']
    search_fields = ['producto__nombre', 'usuario__username', 'titulo', 'comentario']
    list_editable = ['verificado']
    readonly_fields = ['fecha_creacion']

