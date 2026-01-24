from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from functools import wraps
import json
from .models import (Producto, Categoria, Subcategoria, Marca, Proveedor, 
                     Estatus, ProductImage, ProductVideo)


# ==================== DECORADORES DE AUTENTICACIÓN ====================

def admin_required(view_func):
    """
    Decorador personalizado para verificar acceso de superusuario.
    Solo permite acceso a usuarios autenticados con is_superuser=True.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verificar si el usuario está autenticado y es superusuario
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder al área de administración.')
            return redirect('productos:admin_login')
        
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para acceder a esta área.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


# ==================== VISTAS DE AUTENTICACIÓN ====================

def admin_login(request):
    """Vista de login para área de administración - Solo superusuarios"""
    # Si ya está autenticado como superuser, redirigir al admin
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('productos:admin_productos')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Por favor completa todos los campos.')
            return render(request, 'admin_login.html')
        
        # Autenticar usando el sistema de Django
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Verificar que sea superusuario
            if user.is_superuser:
                # Login exitoso
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.get_full_name() or user.username}!')
                
                # Redirigir a la página solicitada o al admin
                next_url = request.GET.get('next', 'productos:admin_productos')
                if next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('productos:admin_productos')
            else:
                messages.error(request, 'No tienes permisos de administrador.')
        else:
            messages.error(request, 'Credenciales incorrectas. Verifica tu usuario y contraseña.')
    
    return render(request, 'admin_login.html')


def admin_logout(request):
    """Vista para cerrar sesión del admin"""
    username = request.user.username if request.user.is_authenticated else 'Usuario'
    logout(request)  # Usa la función logout de Django
    messages.success(request, f'Sesión cerrada exitosamente, {username}.')
    return redirect('home')


# ==================== VISTAS PÚBLICAS ====================

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

@admin_required
def admin_productos(request):
    """Vista para listar productos en el admin"""
    productos = Producto.objects.all().select_related(
        'categoria', 'subcategoria', 'marca', 'proveedor', 'estatus'
    ).order_by('-fecha_creacion')
    
    context = {
        'productos': productos,
    }
    return render(request, 'admin_lista_productos.html', context)


@admin_required
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


@admin_required
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


@admin_required
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
        producto.sku = request.POST.get('sku', '')
        producto.descripcion_corta = request.POST.get('descripcion_corta', '')
        producto.descripcion = request.POST.get('descripcion', '')
        origen_raw = request.POST.get('origen', '') or ''
        # Mantener solo letras y separadores comunes (espacios/guion/apóstrofe)
        origen_clean = ''.join(ch for ch in origen_raw if ch.isalpha() or ch in " -'")
        producto.origen = ' '.join(origen_clean.split())
        producto.dimensiones = request.POST.get('dimensiones', '')
        producto.garantia = request.POST.get('garantia', '')
        
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
        
        # Asignar checkboxes (solo activo y destacado ahora)
        producto.activo = 'activo' in request.POST
        producto.destacado = 'destacado' in request.POST
        
        # Establecer valores por defecto para disponible y en_oferta
        producto.disponible = True  # Siempre disponible por defecto
        
        # En oferta se determina autom\u00e1ticamente si hay precio_oferta
        producto.en_oferta = bool(producto.precio_oferta and producto.precio_oferta > 0)
        
        # Manejar archivos
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
            
        if 'video' in request.FILES:
            producto.video = request.FILES['video']
            
        if 'ficha_tecnica' in request.FILES:
            producto.ficha_tecnica = request.FILES['ficha_tecnica']
        
        producto.save()
        
        # Manejar eliminación de imágenes de galería
        remove_gallery_images = request.POST.get('remove_gallery_images', '')
        if remove_gallery_images:
            image_ids = [int(id) for id in remove_gallery_images.split(',') if id]
            ProductImage.objects.filter(id__in=image_ids, producto=producto).delete()
        
        # Manejar nuevas imágenes de galería
        if 'imagenes_galeria' in request.FILES:
            imagenes = request.FILES.getlist('imagenes_galeria')
            for idx, imagen in enumerate(imagenes):
                ProductImage.objects.create(
                    producto=producto,
                    image=imagen,
                    order=idx
                )
        
        # Manejar eliminación de videos
        remove_videos = request.POST.get('remove_videos', '')
        if remove_videos:
            video_ids = [int(id) for id in remove_videos.split(',') if id]
            ProductVideo.objects.filter(id__in=video_ids, producto=producto).delete()
        
        # Manejar nuevos videos
        if 'videos_galeria' in request.FILES:
            videos = request.FILES.getlist('videos_galeria')
            for idx, video in enumerate(videos):
                ProductVideo.objects.create(
                    producto=producto,
                    video=video,
                    order=idx
                )
        
        messages.success(request, mensaje)
        
    return redirect('productos:admin_productos')


@admin_required
@require_POST
def toggle_producto_status(request, producto_id):
    """Vista AJAX para cambiar el estado activo/inactivo de un producto"""
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        
        # Leer el estado desde el JSON body
        data = json.loads(request.body)
        nuevo_estado = data.get('activo', not producto.activo)
        
        # Actualizar el estado
        producto.activo = nuevo_estado
        producto.save()
        
        return JsonResponse({
            'success': True,
            'activo': producto.activo,
            'message': f'Producto {"activado" if producto.activo else "desactivado"} exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@admin_required
def eliminar_producto(request, producto_id):
    """Vista para eliminar un producto"""
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado exitosamente')
    
    return redirect('productos:admin_productos')


# ==================== VISTAS DE TAXONOMÍAS ====================


@admin_required
def admin_taxonomias(request):
    """Vista para gestionar categorías y subcategorías"""
    categorias = Categoria.objects.prefetch_related(
        'subcategorias'
    ).annotate(
        num_subcategorias=Count('subcategorias'),
        num_productos=Count('productos')
    ).order_by('nombre')
    
    context = {
        'categorias': categorias,
    }
    return render(request, 'admin_taxonomias.html', context)


@admin_required
def crear_categoria(request):
    """Vista para crear una nueva categoría"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not nombre:
            messages.error(request, 'El nombre de la categoría es obligatorio')
            return redirect('productos:admin_taxonomias')
        
        try:
            # Verificar si ya existe
            if Categoria.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f'Ya existe una categoría con el nombre "{nombre}"')
                return redirect('productos:admin_taxonomias')
            
            # Crear categoría
            categoria = Categoria.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                activo=True
            )
            
            # Manejar imagen si existe
            if 'imagen' in request.FILES:
                categoria.imagen = request.FILES['imagen']
                categoria.save()
            
            messages.success(request, f'Categoría "{nombre}" creada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear la categoría: {str(e)}')
    
    return redirect('productos:admin_taxonomias')


@admin_required
def editar_categoria(request, categoria_id):
    """Vista para editar una categoría existente"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not nombre:
            messages.error(request, 'El nombre de la categoría es obligatorio')
            return redirect('productos:admin_taxonomias')
        
        try:
            # Verificar duplicados (excluyendo la categoría actual)
            if Categoria.objects.filter(nombre__iexact=nombre).exclude(id=categoria_id).exists():
                messages.error(request, f'Ya existe otra categoría con el nombre "{nombre}"')
                return redirect('productos:admin_taxonomias')
            
            # Actualizar datos
            categoria.nombre = nombre
            categoria.descripcion = descripcion
            
            # Manejar imagen
            if 'imagen' in request.FILES:
                # Eliminar imagen anterior si existe
                if categoria.imagen:
                    categoria.imagen.delete(save=False)
                categoria.imagen = request.FILES['imagen']
            
            categoria.save()
            
            messages.success(request, f'Categoría "{nombre}" actualizada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar la categoría: {str(e)}')
    
    return redirect('productos:admin_taxonomias')


@admin_required
def eliminar_categoria(request, categoria_id):
    """Vista para eliminar una categoría"""
    if request.method == 'POST':
        categoria = get_object_or_404(Categoria, id=categoria_id)
        nombre = categoria.nombre
        
        try:
            # Verificar si tiene productos asociados
            num_productos = categoria.productos.count()
            num_subcategorias = categoria.subcategorias.count()
            
            if num_productos > 0:
                messages.warning(
                    request, 
                    f'La categoría "{nombre}" tiene {num_productos} productos asociados. '
                    f'Los productos quedarán sin categoría.'
                )
            
            if num_subcategorias > 0:
                messages.warning(
                    request,
                    f'La categoría "{nombre}" tiene {num_subcategorias} subcategorías. '
                    f'Las subcategorías también serán eliminadas.'
                )
            
            # Eliminar imagen si existe
            if categoria.imagen:
                categoria.imagen.delete(save=False)
            
            categoria.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar la categoría: {str(e)}')
    
    return redirect('productos:admin_taxonomias')


@admin_required
def crear_subcategoria(request):
    """Vista para crear una nueva subcategoría"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        categoria_id = request.POST.get('categoria_padre')
        
        if not nombre:
            messages.error(request, 'El nombre de la subcategoría es obligatorio')
            return redirect('productos:admin_taxonomias')
        
        if not categoria_id:
            messages.error(request, 'Debe seleccionar una categoría padre')
            return redirect('productos:admin_taxonomias')
        
        try:
            categoria = get_object_or_404(Categoria, id=categoria_id)
            
            # Verificar si ya existe en esa categoría
            if Subcategoria.objects.filter(
                nombre__iexact=nombre, 
                categoria=categoria
            ).exists():
                messages.error(
                    request, 
                    f'Ya existe una subcategoría "{nombre}" en la categoría "{categoria.nombre}"'
                )
                return redirect('productos:admin_taxonomias')
            
            # Crear subcategoría
            subcategoria = Subcategoria.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                activo=True
            )
            
            messages.success(
                request, 
                f'Subcategoría "{nombre}" creada exitosamente en "{categoria.nombre}"'
            )
        except Exception as e:
            messages.error(request, f'Error al crear la subcategoría: {str(e)}')
    
    return redirect('productos:admin_taxonomias')


@admin_required
def editar_subcategoria(request, subcategoria_id):
    """Vista para editar una subcategoría existente"""
    subcategoria = get_object_or_404(Subcategoria, id=subcategoria_id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not nombre:
            messages.error(request, 'El nombre de la subcategoría es obligatorio')
            return redirect('productos:admin_taxonomias')
        
        try:
            # Verificar duplicados en la misma categoría (excluyendo la actual)
            if Subcategoria.objects.filter(
                nombre__iexact=nombre,
                categoria=subcategoria.categoria
            ).exclude(id=subcategoria_id).exists():
                messages.error(
                    request,
                    f'Ya existe otra subcategoría "{nombre}" en esta categoría'
                )
                return redirect('productos:admin_taxonomias')
            
            # Actualizar datos
            subcategoria.nombre = nombre
            subcategoria.descripcion = descripcion
            subcategoria.save()
            
            messages.success(request, f'Subcategoría "{nombre}" actualizada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar la subcategoría: {str(e)}')
    
    return redirect('productos:admin_taxonomias')


@admin_required
def eliminar_subcategoria(request, subcategoria_id):
    """Vista para eliminar una subcategoría"""
    if request.method == 'POST':
        subcategoria = get_object_or_404(Subcategoria, id=subcategoria_id)
        nombre = subcategoria.nombre
        
        try:
            # Verificar productos asociados
            num_productos = subcategoria.productos.count()
            
            if num_productos > 0:
                messages.warning(
                    request,
                    f'La subcategoría "{nombre}" tiene {num_productos} productos asociados. '
                    f'Los productos quedarán sin subcategoría.'
                )
            
            subcategoria.delete()
            messages.success(request, f'Subcategoría "{nombre}" eliminada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar la subcategoría: {str(e)}')
    
    return redirect('productos:admin_taxonomias')



@admin_required
@require_POST
def toggle_categoria_status(request, categoria_id):
    """Vista AJAX para cambiar el estado activo/inactivo de una categoría"""
    try:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        data = json.loads(request.body)
        nuevo_estado = data.get('activo', not categoria.activo)
        
        categoria.activo = nuevo_estado
        categoria.save()
        
        return JsonResponse({
            'success': True,
            'activo': categoria.activo,
            'message': f'Categoría {"activada" if categoria.activo else "desactivada"} exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)



@admin_required
@require_POST
def toggle_subcategoria_status(request, subcategoria_id):
    """Vista AJAX para cambiar el estado activo/inactivo de una subcategoría"""
    try:
        subcategoria = get_object_or_404(Subcategoria, id=subcategoria_id)
        data = json.loads(request.body)
        nuevo_estado = data.get('activo', not subcategoria.activo)
        
        subcategoria.activo = nuevo_estado
        subcategoria.save()
        
        return JsonResponse({
            'success': True,
            'activo': subcategoria.activo,
            'message': f'Subcategoría {"activada" if subcategoria.activo else "desactivada"} exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def buscar_productos(request):
    """Vista para búsqueda de productos con AJAX"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({
            'success': False,
            'message': 'Ingresa al menos 2 caracteres para buscar',
            'productos': []
        })
    
    # Buscar en múltiples campos
    productos = Producto.objects.filter(
        Q(nombre__icontains=query) |
        Q(descripcion_corta__icontains=query) |
        Q(descripcion__icontains=query) |
        Q(sku__icontains=query) |
        Q(categoria__nombre__icontains=query) |
        Q(subcategoria__nombre__icontains=query) |
        Q(marca__nombre__icontains=query),
        activo=True,
        disponible=True
    ).select_related(
        'categoria', 
        'subcategoria', 
        'marca'
    ).prefetch_related('imagenes_galeria')[:20]
    
    # Serializar resultados
    resultados = []
    for producto in productos:
        # Obtener imagen principal
        imagen_url = None
        if producto.imagen:
            imagen_url = producto.imagen.url
        elif producto.imagenes_galeria.exists():
            imagen_url = producto.imagenes_galeria.first().imagen.url
        
        resultados.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'slug': producto.slug,
            'descripcion_corta': producto.descripcion_corta or '',
            'precio': str(producto.precio_final),
            'precio_oferta': str(producto.precio_oferta) if producto.tiene_descuento else None,
            'descuento': producto.porcentaje_descuento if producto.en_oferta else None,
            'imagen': imagen_url,
            'categoria': producto.categoria.nombre if producto.categoria else '',
            'marca': producto.marca.nombre if producto.marca else '',
            'url': f'/productos/{producto.slug}/',
            'stock': producto.stock,
            'destacado': producto.destacado,
            'en_oferta': producto.en_oferta,
        })
    
    return JsonResponse({
        'success': True,
        'count': len(resultados),
        'query': query,
        'productos': resultados
    })
