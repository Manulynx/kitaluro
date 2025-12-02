from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Producto, Categoria, Marca

def index(request):
    """Vista para mostrar la lista de productos"""
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return get_productos_json(request)
    
    # Si es petición normal, devolver template
    categorias = Categoria.objects.filter(activo=True)
    marcas = Marca.objects.filter(activo=True)
    
    context = {
        'page_title': 'Catálogo de Productos',
        'categorias': categorias,
        'marcas': marcas,
    }
    return render(request, 'index.html', context)


def get_productos_json(request):
    """API para obtener productos en formato JSON"""
    # Obtener parámetros de filtrado
    categoria_slug = request.GET.get('categoria')
    marca_id = request.GET.get('marca')
    busqueda = request.GET.get('q')
    
    # Filtrar productos
    productos = Producto.objects.filter(activo=True, disponible=True).select_related('categoria', 'marca')
    
    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)
    
    if marca_id:
        productos = productos.filter(marca_id=marca_id)
    
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda) | productos.filter(descripcion__icontains=busqueda)
    
    # Paginación
    paginator = Paginator(productos, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Serializar productos
    productos_data = []
    for producto in page_obj:
        # Obtener primera imagen
        imagen_principal = None
        primera_media = producto.medias.filter(tipo='imagen').first()
        if primera_media and primera_media.imagen:
            imagen_principal = primera_media.imagen.url
        
        productos_data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'slug': producto.slug,
            'descripcion_corta': producto.descripcion_corta,
            'precio': str(producto.precio),
            'precio_oferta': str(producto.precio_oferta) if producto.precio_oferta else None,
            'stock': producto.stock,
            'imagen_principal': imagen_principal,
            'rating': 4.0,  # Placeholder, calcular promedio real si es necesario
            'categoria': producto.categoria.nombre if producto.categoria else None,
            'marca': producto.marca.nombre if producto.marca else None,
        })
    
    return JsonResponse({
        'productos': productos_data,
        'total': paginator.count,
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    })


def detalle(request, slug):
    """Vista para mostrar el detalle de un producto"""
    # Si es petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return get_producto_detalle_json(request, slug)
    
    # Si es petición normal, devolver template vacío que JavaScript llenará
    return render(request, 'detalle.html', {})


def get_producto_detalle_json(request, slug):
    """API para obtener detalle de producto en formato JSON"""
    producto = get_object_or_404(Producto, slug=slug, activo=True)
    
    # Productos relacionados
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        activo=True,
        disponible=True
    ).exclude(id=producto.id)[:4]
    
    # Serializar imágenes
    imagenes = []
    for media in producto.medias.filter(tipo='imagen'):
        if media.imagen:
            imagenes.append({
                'url': media.imagen.url,
                'alt': media.alt_text or producto.nombre
            })
    
    # Serializar valoraciones
    valoraciones = []
    for val in producto.valoraciones.all():
        valoraciones.append({
            'usuario': val.usuario.username if val.usuario else None,
            'puntuacion': val.puntuacion,
            'titulo': val.titulo,
            'comentario': val.comentario,
            'fecha': val.fecha_creacion.strftime('%d/%m/%Y'),
            'verificado': val.verificado
        })
    
    # Serializar productos relacionados
    relacionados_data = []
    for prod in productos_relacionados:
        imagen_principal = None
        primera_media = prod.medias.filter(tipo='imagen').first()
        if primera_media and primera_media.imagen:
            imagen_principal = primera_media.imagen.url
        
        relacionados_data.append({
            'id': prod.id,
            'nombre': prod.nombre,
            'slug': prod.slug,
            'precio': str(prod.precio),
            'precio_oferta': str(prod.precio_oferta) if prod.precio_oferta else None,
            'imagen_principal': imagen_principal
        })
    
    # Datos completos del producto
    data = {
        'id': producto.id,
        'nombre': producto.nombre,
        'slug': producto.slug,
        'descripcion_corta': producto.descripcion_corta,
        'descripcion': producto.descripcion,
        'precio': str(producto.precio),
        'precio_oferta': str(producto.precio_oferta) if producto.precio_oferta else None,
        'tiene_descuento': producto.tiene_descuento,
        'porcentaje_descuento': producto.porcentaje_descuento,
        'stock': producto.stock,
        'en_stock': producto.en_stock,
        'sku': producto.sku,
        'peso': str(producto.peso) if producto.peso else None,
        'dimensiones': producto.dimensiones,
        'destacado': producto.destacado,
        'categoria': producto.categoria.nombre if producto.categoria else None,
        'categoria_slug': producto.categoria.slug if producto.categoria else None,
        'marca': producto.marca.nombre if producto.marca else None,
        'imagenes': imagenes,
        'valoraciones': valoraciones,
        'total_valoraciones': producto.valoraciones.count(),
        'productos_relacionados': relacionados_data
    }
    
    return JsonResponse(data)
