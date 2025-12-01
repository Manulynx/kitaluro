from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Producto, Categoria, Marca

def index(request):
    """Vista para mostrar la lista de productos"""
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
    
    # Obtener productos destacados
    productos_destacados = Producto.objects.filter(activo=True, disponible=True, destacado=True)[:6]
    
    # Paginación
    paginator = Paginator(productos, 12)  # 12 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener categorías y marcas para filtros
    categorias = Categoria.objects.filter(activo=True)
    marcas = Marca.objects.filter(activo=True)
    
    context = {
        'page_title': 'Catálogo de Productos',
        'productos': page_obj,
        'productos_destacados': productos_destacados,
        'categorias': categorias,
        'marcas': marcas,
        'categoria_actual': categoria_slug,
        'busqueda': busqueda,
    }
    return render(request, 'index.html', context)
