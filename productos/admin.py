from django.contrib import admin
from django.utils.html import format_html
from .models import (Categoria, Subcategoria, Marca, Proveedor, Estatus, 
                     Producto, ProductImage, ProductVideo, Valoracion)

# Register your models here.

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'id_unico', 'activo', 'count_productos', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'id_unico']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['activo']
    readonly_fields = ['id_unico', 'fecha_creacion']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'activo', 'count_subcategorias', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['activo']


@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'slug', 'activo', 'count_productos', 'fecha_creacion']
    list_filter = ['activo', 'categoria', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['activo']


@admin.register(Estatus)
class EstatusAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'activo', 'count_productos', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['activo']


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['activo']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order', 'is_main']


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1
    fields = ['video', 'title', 'description', 'order']


class ValoracionInline(admin.TabularInline):
    model = Valoracion
    extra = 0
    fields = ['usuario', 'puntuacion', 'titulo', 'comentario', 'verificado']
    readonly_fields = ['fecha_creacion']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'sku', 'categoria', 'subcategoria', 'marca', 'proveedor', 'precio_display', 'stock', 'disponible', 'destacado', 'en_oferta', 'fecha_creacion']
    list_filter = ['categoria', 'subcategoria', 'marca', 'proveedor', 'estatus', 'disponible', 'destacado', 'en_oferta', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'descripcion_corta', 'sku', 'origen']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['disponible', 'destacado', 'en_oferta', 'stock']
    readonly_fields = ['sku', 'fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'slug', 'sku', 'descripcion_corta', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('categoria', 'subcategoria', 'marca', 'proveedor', 'estatus')
        }),
        ('Precios e Inventario', {
            'fields': ('precio', 'precio_oferta', 'stock')
        }),
        ('Multimedia y Documentación', {
            'fields': ('imagen', 'video', 'ficha_tecnica'),
            'classes': ('collapse',)
        }),
        ('Características', {
            'fields': ('peso', 'dimensiones', 'origen'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('disponible', 'activo', 'destacado', 'en_oferta')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductVideoInline, ValoracionInline]
    
    def precio_display(self, obj):
        if obj.precio:
            if obj.precio_oferta:
                return format_html(
                    '<span style="text-decoration: line-through; color: #999;">${}</span> <strong style="color: #28a745;">${}</strong>',
                    obj.precio, obj.precio_oferta
                )
            return f'${obj.precio}'
        return '-'
    precio_display.short_description = 'Precio'


@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ['producto', 'usuario', 'puntuacion', 'titulo', 'verificado', 'fecha_creacion']
    list_filter = ['puntuacion', 'verificado', 'fecha_creacion']
    search_fields = ['producto__nombre', 'usuario__username', 'titulo', 'comentario']
    list_editable = ['verificado']
    readonly_fields = ['fecha_creacion']

