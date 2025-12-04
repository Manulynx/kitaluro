from django.shortcuts import render
from productos.models import Producto

def home(request):
    """Vista para la página de inicio"""
    # Obtener productos destacados o en oferta
    productos_destacados = Producto.objects.filter(
        activo=True,
        disponible=True
    ).select_related('categoria', 'marca').prefetch_related('imagenes_galeria')[:6]
    
    context = {
        'productos': productos_destacados
    }
    return render(request, 'home.html', context)

def contacto(request):
    """Vista para la página de contacto"""
    return render(request, 'contacto.html')