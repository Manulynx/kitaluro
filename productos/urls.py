from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', views.admin_productos, name='admin_productos'),
    path('admin/nuevo/', views.nuevo_producto, name='nuevo_producto'),
    path('admin/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('admin/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('admin/toggle-status/<int:producto_id>/', views.toggle_producto_status, name='toggle_producto_status'),
    
    # URLs de Taxonomías
    path('admin/taxonomias/', views.admin_taxonomias, name='admin_taxonomias'),
    path('admin/taxonomias/categoria/crear/', views.crear_categoria, name='crear_categoria'),
    path('admin/taxonomias/categoria/<int:categoria_id>/editar/', views.editar_categoria, name='editar_categoria'),
    path('admin/taxonomias/categoria/<int:categoria_id>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),
    path('admin/taxonomias/categoria/<int:categoria_id>/toggle/', views.toggle_categoria_status, name='toggle_categoria_status'),
    
    path('admin/taxonomias/subcategoria/crear/', views.crear_subcategoria, name='crear_subcategoria'),
    path('admin/taxonomias/subcategoria/<int:subcategoria_id>/editar/', views.editar_subcategoria, name='editar_subcategoria'),
    path('admin/taxonomias/subcategoria/<int:subcategoria_id>/eliminar/', views.eliminar_subcategoria, name='eliminar_subcategoria'),
    path('admin/taxonomias/subcategoria/<int:subcategoria_id>/toggle/', views.toggle_subcategoria_status, name='toggle_subcategoria_status'),
    
    # APIs
    path('api/productos/', views.get_productos_json, name='api_productos'),
    path('api/buscar/', views.buscar_productos, name='buscar_productos'),
    path('<slug:slug>/json/', views.get_producto_detalle_json, name='detalle_json'),
    path('<slug:slug>/', views.detalle, name='detalle'),
]
