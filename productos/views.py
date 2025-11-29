from django.shortcuts import render

def index(request):
    """Vista para mostrar la lista de productos"""
    context = {
        'page_title': 'Catálogo de Productos',
    }
    return render(request, 'index.html', context)
