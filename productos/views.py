from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Avg
from .models import (Producto, Categoria, Subcategoria, Marca, Proveedor, 
                     Estatus, ProductImage, ProductVideo)

def index(request):
    """Vista para mostrar la lista de productos"""
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return get_productos_json(request)
    
    # Si es petición normal, devolver template
    categorias = Categoria.objects.filter(activo=True)
    subcategorias = Subcategoria.objects.filter(activo=True).select_related('categoria')
    marcas = Marca.objects.filter(activo=True)
    proveedores = Proveedor.objects.filter(activo=True)
    estatus_list = Estatus.objects.filter(activo=True)
    
    # Obtener todos los productos activos y disponibles con optimización
    productos = Producto.objects.filter(
        activo=True, 
        disponible=True
    ).select_related(
        'categoria', 
        'subcategoria', 
        'marca', 
        'proveedor', 
        'estatus'
    ).prefetch_related(
        'imagenes_galeria',
        'valoraciones'
    ).order_by('-destacado', '-en_oferta', '-fecha_creacion')
    
    # Productos destacados y en oferta para destacar en la UI
    productos_destacados = Producto.get_featured_products()[:8]
    productos_oferta = Producto.get_on_sale_products()[:8]
    
    context = {
        'page_title': 'Catálogo de Productos',
        'productos': productos,  # Agregar todos los productos
        'categorias': categorias,
        'subcategorias': subcategorias,
        'marcas': marcas,
        'proveedores': proveedores,
        'estatus_list': estatus_list,
        'productos_destacados': productos_destacados,
        'productos_oferta': productos_oferta,
    }
    return render(request, 'index.html', context)


def get_productos_json(request):
    """API para obtener productos en formato JSON"""
    # Obtener parámetros de filtrado
    categoria_slug = request.GET.get('categoria')
    subcategoria_slug = request.GET.get('subcategoria')
    marca_id = request.GET.get('marca')
    proveedor_id = request.GET.get('proveedor')
    estatus_id = request.GET.get('estatus')
    destacado = request.GET.get('destacado')
    en_oferta = request.GET.get('en_oferta')
    busqueda = request.GET.get('q')
    orden = request.GET.get('orden', '-fecha_creacion')  # Por defecto más recientes
    
    # Filtrar productos
    productos = Producto.objects.filter(
        activo=True, 
        disponible=True
    ).select_related(
        'categoria', 
        'subcategoria', 
        'marca', 
        'proveedor', 
        'estatus'
    )
    
    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)
    
    if subcategoria_slug:
        productos = productos.filter(subcategoria__slug=subcategoria_slug)
    
    if marca_id:
        productos = productos.filter(marca_id=marca_id)
    
    if proveedor_id:
        productos = productos.filter(proveedor_id=proveedor_id)
    
    if estatus_id:
        productos = productos.filter(estatus_id=estatus_id)
    
    if destacado == 'true':
        productos = productos.filter(destacado=True)
    
    if en_oferta == 'true':
        productos = productos.filter(en_oferta=True)
    
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda) |
            Q(descripcion_corta__icontains=busqueda) |
            Q(sku__icontains=busqueda)
        )
    
    # Ordenamiento
    orden_validos = {
        'precio_asc': 'precio',
        'precio_desc': '-precio',
        'nombre_asc': 'nombre',
        'nombre_desc': '-nombre',
        'recientes': '-fecha_creacion',
        'antiguos': 'fecha_creacion',
    }
    if orden in orden_validos:
        productos = productos.order_by(orden_validos[orden])
    else:
        productos = productos.order_by('-destacado', '-en_oferta', '-fecha_creacion')
    
    # Paginación
    paginator = Paginator(productos, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Serializar productos
    productos_data = []
    for producto in page_obj:
        # Obtener imagen principal usando el método del modelo
        imagen_principal = None
        main_image = producto.get_main_image()
        if main_image:
            imagen_principal = main_image.url
        elif producto.imagen:
            imagen_principal = producto.imagen.url
        
        # Calcular rating promedio
        rating_promedio = producto.valoraciones.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
        
        # Obtener badges de estado
        badges = producto.get_status_badges()
        
        productos_data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'slug': producto.slug,
            'descripcion_corta': producto.descripcion_corta,
            'precio': str(producto.precio) if producto.precio else None,
            'precio_oferta': str(producto.precio_oferta) if producto.precio_oferta else None,
            'tiene_descuento': producto.tiene_descuento,
            'porcentaje_descuento': producto.porcentaje_descuento,
            'stock': producto.stock,
            'en_stock': producto.en_stock,
            'imagen_principal': imagen_principal,
            'rating': round(rating_promedio, 1),
            'total_valoraciones': producto.valoraciones.count(),
            'categoria': producto.categoria.nombre if producto.categoria else None,
            'categoria_slug': producto.categoria.slug if producto.categoria else None,
            'subcategoria': producto.subcategoria.nombre if producto.subcategoria else None,
            'subcategoria_slug': producto.subcategoria.slug if producto.subcategoria else None,
            'marca': producto.marca.nombre if producto.marca else None,
            'proveedor': producto.proveedor.nombre if producto.proveedor else None,
            'estatus': producto.estatus.nombre if producto.estatus else None,
            'origen': producto.origen,
            'destacado': producto.destacado,
            'en_oferta': producto.en_oferta,
            'badges': badges,
            'url': producto.get_absolute_url(),
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
    
    # Obtener el producto
    producto = get_object_or_404(Producto, slug=slug, activo=True)
    
    # Productos relacionados (misma categoría o subcategoría)
    productos_relacionados = Producto.objects.filter(
        activo=True,
        disponible=True
    ).filter(
        Q(categoria=producto.categoria) | 
        Q(subcategoria=producto.subcategoria) |
        Q(marca=producto.marca)
    ).exclude(id=producto.id).distinct()[:6]
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
    }
    
    return render(request, 'detalle.html', context)


def get_producto_detalle_json(request, slug):
    """API para obtener detalle de producto en formato JSON"""
    producto = get_object_or_404(Producto, slug=slug, activo=True)
    
    # Productos relacionados (misma categoría o subcategoría)
    productos_relacionados = Producto.objects.filter(
        activo=True,
        disponible=True
    ).filter(
        Q(categoria=producto.categoria) | 
        Q(subcategoria=producto.subcategoria) |
        Q(marca=producto.marca)
    ).exclude(id=producto.id).distinct()[:6]
    
    # Serializar imágenes desde ProductImage (galería)
    imagenes = []
    for img in producto.imagenes_galeria.all():
        imagenes.append({
            'url': img.image.url,
            'alt': img.alt_text or producto.nombre,
            'is_main': img.is_main,
            'order': img.order
        })
    
    # Agregar imagen principal del modelo si existe y no hay galería
    if producto.imagen and not imagenes:
        imagenes.append({
            'url': producto.imagen.url,
            'alt': producto.nombre,
            'is_main': True,
            'order': 0
        })
    
    # Serializar videos desde ProductVideo
    videos = []
    for vid in producto.videos_galeria.all():
        videos.append({
            'url': vid.video.url,
            'title': vid.title,
            'description': vid.description,
            'order': vid.order
        })
    
    # Video principal del modelo
    if producto.video and not videos:
        videos.append({
            'url': producto.video.url,
            'title': 'Video del producto',
            'description': '',
            'order': 0
        })
    
    # Serializar valoraciones
    valoraciones = []
    for val in producto.valoraciones.all():
        valoraciones.append({
            'usuario': val.usuario.username if val.usuario else 'Anónimo',
            'puntuacion': val.puntuacion,
            'titulo': val.titulo,
            'comentario': val.comentario,
            'fecha': val.fecha_creacion.strftime('%d/%m/%Y'),
            'verificado': val.verificado
        })
    
    # Calcular estadísticas de valoraciones
    rating_promedio = producto.valoraciones.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
    distribucion_rating = {
        '5': producto.valoraciones.filter(puntuacion=5).count(),
        '4': producto.valoraciones.filter(puntuacion=4).count(),
        '3': producto.valoraciones.filter(puntuacion=3).count(),
        '2': producto.valoraciones.filter(puntuacion=2).count(),
        '1': producto.valoraciones.filter(puntuacion=1).count(),
    }
    
    # Serializar productos relacionados
    relacionados_data = []
    for prod in productos_relacionados:
        # Obtener imagen principal
        imagen_principal = None
        main_image = prod.get_main_image()
        if main_image:
            imagen_principal = main_image.url
        elif prod.imagen:
            imagen_principal = prod.imagen.url
        
        # Rating del producto relacionado
        rating_rel = prod.valoraciones.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
        
        relacionados_data.append({
            'id': prod.id,
            'nombre': prod.nombre,
            'slug': prod.slug,
            'precio': str(prod.precio) if prod.precio else None,
            'precio_oferta': str(prod.precio_oferta) if prod.precio_oferta else None,
            'tiene_descuento': prod.tiene_descuento,
            'porcentaje_descuento': prod.porcentaje_descuento,
            'imagen_principal': imagen_principal,
            'rating': round(rating_rel, 1),
            'destacado': prod.destacado,
            'en_oferta': prod.en_oferta,
            'url': prod.get_absolute_url(),
        })
    
    # Datos completos del producto
    data = {
        'id': producto.id,
        'nombre': producto.nombre,
        'slug': producto.slug,
        'descripcion_corta': producto.descripcion_corta,
        'descripcion': producto.descripcion,
        'precio': str(producto.precio) if producto.precio else None,
        'precio_oferta': str(producto.precio_oferta) if producto.precio_oferta else None,
        'tiene_descuento': producto.tiene_descuento,
        'porcentaje_descuento': producto.porcentaje_descuento,
        'stock': producto.stock,
        'en_stock': producto.en_stock,
        'sku': producto.sku,
        'peso': str(producto.peso) if producto.peso else None,
        'dimensiones': producto.dimensiones,
        'origen': producto.origen,
        'destacado': producto.destacado,
        'en_oferta': producto.en_oferta,
        'categoria': producto.categoria.nombre if producto.categoria else None,
        'categoria_slug': producto.categoria.slug if producto.categoria else None,
        'subcategoria': producto.subcategoria.nombre if producto.subcategoria else None,
        'subcategoria_slug': producto.subcategoria.slug if producto.subcategoria else None,
        'marca': producto.marca.nombre if producto.marca else None,
        'marca_slug': producto.marca.slug if producto.marca else None,
        'proveedor': producto.proveedor.nombre if producto.proveedor else None,
        'proveedor_slug': producto.proveedor.slug if producto.proveedor else None,
        'estatus': producto.estatus.nombre if producto.estatus else None,
        'ficha_tecnica': producto.ficha_tecnica.url if producto.ficha_tecnica else None,
        'imagenes': imagenes,
        'videos': videos,
        'valoraciones': valoraciones,
        'rating_promedio': round(rating_promedio, 1),
        'distribucion_rating': distribucion_rating,
        'total_valoraciones': producto.valoraciones.count(),
        'productos_relacionados': relacionados_data,
        'badges': producto.get_status_badges(),
        'url': producto.get_absolute_url(),
        'fecha_creacion': producto.fecha_creacion.strftime('%d/%m/%Y'),
        'fecha_actualizacion': producto.fecha_actualizacion.strftime('%d/%m/%Y'),
    }
    
    return JsonResponse(data)


# ==================== VISTAS DE ADMINISTRACIÓN ====================

def admin_productos(request):
    """Vista para listar productos en el admin"""
    productos = Producto.objects.all().select_related(
        'categoria', 'subcategoria', 'marca', 'proveedor', 'estatus'
    ).order_by('-fecha_creacion')
    
    context = {
        'productos': productos,
    }
    return render(request, 'admin_lista_productos.html', context)


def nuevo_producto(request):
    """Vista para crear un nuevo producto"""
    if request.method == 'POST':
        return guardar_producto(request)
    
    # GET: Mostrar formulario vacío
    categorias = Categoria.objects.filter(activo=True).order_by('nombre')
    subcategorias = Subcategoria.objects.filter(activo=True).select_related('categoria').order_by('nombre')
    marcas = Marca.objects.filter(activo=True).order_by('nombre')
    proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
    estatus_list = Estatus.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'categorias': categorias,
        'subcategorias': subcategorias,
        'marcas': marcas,
        'proveedores': proveedores,
        'estatus_list': estatus_list,
    }
    return render(request, 'admin_form_producto.html', context)


def editar_producto(request, producto_id):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        return guardar_producto(request, producto_id)
    
    # GET: Mostrar formulario con datos del producto
    categorias = Categoria.objects.filter(activo=True).order_by('nombre')
    subcategorias = Subcategoria.objects.filter(activo=True).select_related('categoria').order_by('nombre')
    marcas = Marca.objects.filter(activo=True).order_by('nombre')
    proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
    estatus_list = Estatus.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'producto': producto,
        'categorias': categorias,
        'subcategorias': subcategorias,
        'marcas': marcas,
        'proveedores': proveedores,
        'estatus_list': estatus_list,
    }
    return render(request, 'admin_form_producto.html', context)


def guardar_producto(request, producto_id=None):
    """Vista para guardar (crear o actualizar) un producto"""
    if request.method == 'POST':
        # Si hay ID, es edición; sino, es creación
        if producto_id:
            producto = get_object_or_404(Producto, id=producto_id)
            mensaje = 'Producto actualizado exitosamente'
        else:
            producto = Producto()
            mensaje = 'Producto creado exitosamente'
        
        # Asignar campos básicos
        producto.nombre = request.POST.get('nombre')
        producto.descripcion_corta = request.POST.get('descripcion_corta', '')
        producto.descripcion = request.POST.get('descripcion', '')
        producto.origen = request.POST.get('origen', '')
        producto.dimensiones = request.POST.get('dimensiones', '')
        
        # Asignar relaciones (ForeignKey)
        categoria_id = request.POST.get('categoria')
        if categoria_id:
            producto.categoria = Categoria.objects.get(id=categoria_id)
        else:
            producto.categoria = None
            
        subcategoria_id = request.POST.get('subcategoria')
        if subcategoria_id:
            producto.subcategoria = Subcategoria.objects.get(id=subcategoria_id)
        else:
            producto.subcategoria = None
            
        marca_id = request.POST.get('marca')
        if marca_id:
            producto.marca = Marca.objects.get(id=marca_id)
        else:
            producto.marca = None
            
        proveedor_id = request.POST.get('proveedor')
        if proveedor_id:
            producto.proveedor = Proveedor.objects.get(id=proveedor_id)
        else:
            producto.proveedor = None
            
        estatus_id = request.POST.get('estatus')
        if estatus_id:
            producto.estatus = Estatus.objects.get(id=estatus_id)
        else:
            producto.estatus = None
        
        # Asignar campos numéricos
        precio = request.POST.get('precio')
        producto.precio = float(precio) if precio else None
        
        precio_oferta = request.POST.get('precio_oferta')
        producto.precio_oferta = float(precio_oferta) if precio_oferta else None
        
        stock = request.POST.get('stock')
        producto.stock = int(stock) if stock else 0
        
        peso = request.POST.get('peso')
        producto.peso = float(peso) if peso else None
        
        # Asignar checkboxes
        producto.disponible = 'disponible' in request.POST
        producto.activo = 'activo' in request.POST
        producto.destacado = 'destacado' in request.POST
        producto.en_oferta = 'en_oferta' in request.POST
        
        # Manejar archivos
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
            
        if 'video' in request.FILES:
            producto.video = request.FILES['video']
            
        if 'ficha_tecnica' in request.FILES:
            producto.ficha_tecnica = request.FILES['ficha_tecnica']
        
        producto.save()
        messages.success(request, mensaje)
        
    return redirect('productos:admin_productos')


def eliminar_producto(request, producto_id):
    """Vista para eliminar un producto"""
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado exitosamente')
    
    return redirect('productos:admin_productos')
