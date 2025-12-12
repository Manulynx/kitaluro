from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', views.admin_productos, name='admin_productos'),
    path('admin/nuevo/', views.nuevo_producto, name='nuevo_producto'),
    path('admin/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('admin/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('api/productos/', views.get_productos_json, name='api_productos'),
    path('<slug:slug>/json/', views.get_producto_detalle_json, name='detalle_json'),
    path('<slug:slug>/', views.detalle, name='detalle'),
]
