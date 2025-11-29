from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.index, name='index'),
    # Agregar más rutas de productos aquí en el futuro
]
