from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/productos/', views.get_productos_json, name='api_productos'),
    path('<slug:slug>/json/', views.get_producto_detalle_json, name='detalle_json'),
    path('<slug:slug>/', views.detalle, name='detalle'),
]
