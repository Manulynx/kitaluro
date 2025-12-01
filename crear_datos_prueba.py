"""
Script para crear datos de prueba en la base de datos
Ejecutar con: python manage.py shell < crear_datos_prueba.py
O: python crear_datos_prueba.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitaluro.settings')
django.setup()

from productos.models import Categoria, Marca, Producto, MediaProducto
from django.contrib.auth.models import User
from decimal import Decimal

def crear_datos_prueba():
    print("🚀 Creando datos de prueba...")
    
    # Crear categorías
    print("\n📁 Creando categorías...")
    categorias = {
        'electronica': Categoria.objects.create(
            nombre='Electrónica',
            slug='electronica',
            descripcion='Productos electrónicos y tecnología',
            activo=True
        ),
        'ropa': Categoria.objects.create(
            nombre='Ropa y Moda',
            slug='ropa-moda',
            descripcion='Ropa, calzado y accesorios',
            activo=True
        ),
        'hogar': Categoria.objects.create(
            nombre='Hogar y Cocina',
            slug='hogar-cocina',
            descripcion='Artículos para el hogar y la cocina',
            activo=True
        ),
        'deportes': Categoria.objects.create(
            nombre='Deportes',
            slug='deportes',
            descripcion='Equipamiento deportivo y fitness',
            activo=True
        ),
        'libros': Categoria.objects.create(
            nombre='Libros',
            slug='libros',
            descripcion='Libros físicos y digitales',
            activo=True
        ),
    }
    print(f"✅ {len(categorias)} categorías creadas")
    
    # Crear marcas
    print("\n🏷️ Creando marcas...")
    marcas = {
        'samsung': Marca.objects.create(nombre='Samsung', descripcion='Electrónica premium', activo=True),
        'nike': Marca.objects.create(nombre='Nike', descripcion='Ropa deportiva', activo=True),
        'adidas': Marca.objects.create(nombre='Adidas', descripcion='Calzado y ropa', activo=True),
        'sony': Marca.objects.create(nombre='Sony', descripcion='Tecnología de entretenimiento', activo=True),
        'ikea': Marca.objects.create(nombre='IKEA', descripcion='Muebles y decoración', activo=True),
        'apple': Marca.objects.create(nombre='Apple', descripcion='Tecnología innovadora', activo=True),
        'zara': Marca.objects.create(nombre='Zara', descripcion='Moda contemporánea', activo=True),
    }
    print(f"✅ {len(marcas)} marcas creadas")
    
    # Crear productos
    print("\n📦 Creando productos...")
    productos = []
    
    # Productos de Electrónica
    productos.append(Producto.objects.create(
        nombre='Smartphone Samsung Galaxy S23',
        slug='samsung-galaxy-s23',
        descripcion_corta='Última generación con cámara de 200MP',
        descripcion='El Samsung Galaxy S23 ofrece una experiencia móvil premium con su pantalla AMOLED de 6.1", procesador Snapdragon 8 Gen 2, y cámara principal de 200MP. Incluye 8GB de RAM y 256GB de almacenamiento.',
        categoria=categorias['electronica'],
        marca=marcas['samsung'],
        precio=Decimal('899.99'),
        precio_oferta=Decimal('799.99'),
        stock=50,
        sku='SAMS23-256-BLK',
        peso=Decimal('0.168'),
        dimensiones='146.3 x 70.9 x 7.6',
        disponible=True,
        destacado=True,
        activo=True
    ))
    
    productos.append(Producto.objects.create(
        nombre='MacBook Pro 14" M3',
        slug='macbook-pro-14-m3',
        descripcion_corta='Potencia profesional con chip M3',
        descripcion='MacBook Pro de 14 pulgadas con chip M3, 16GB de memoria unificada y SSD de 512GB. Pantalla Liquid Retina XDR y batería de hasta 17 horas.',
        categoria=categorias['electronica'],
        marca=marcas['apple'],
        precio=Decimal('1999.99'),
        stock=25,
        sku='MBP14-M3-512',
        peso=Decimal('1.55'),
        dimensiones='31.26 x 22.12 x 1.55',
        disponible=True,
        destacado=True,
        activo=True
    ))
    
    productos.append(Producto.objects.create(
        nombre='Auriculares Sony WH-1000XM5',
        slug='sony-wh-1000xm5',
        descripcion_corta='Cancelación de ruido líder en la industria',
        descripcion='Auriculares inalámbricos premium con la mejor cancelación de ruido del mercado. 30 horas de batería, audio de alta resolución y diseño ergonómico.',
        categoria=categorias['electronica'],
        marca=marcas['sony'],
        precio=Decimal('399.99'),
        precio_oferta=Decimal('349.99'),
        stock=75,
        sku='SONY-WH1000XM5',
        peso=Decimal('0.25'),
        disponible=True,
        destacado=True,
        activo=True
    ))
    
    # Productos de Ropa
    productos.append(Producto.objects.create(
        nombre='Zapatillas Nike Air Max 90',
        slug='nike-air-max-90',
        descripcion_corta='Clásicas zapatillas con estilo retro',
        descripcion='Las icónicas Nike Air Max 90 combinan comodidad y estilo. Diseño clásico con amortiguación Air visible y materiales duraderos.',
        categoria=categorias['ropa'],
        marca=marcas['nike'],
        precio=Decimal('129.99'),
        stock=100,
        sku='NIKE-AM90-WHT-42',
        peso=Decimal('0.85'),
        disponible=True,
        destacado=False,
        activo=True
    ))
    
    productos.append(Producto.objects.create(
        nombre='Chaqueta Adidas Originals',
        slug='adidas-chaqueta-originals',
        descripcion_corta='Chaqueta deportiva con estilo urbano',
        descripcion='Chaqueta Adidas Originals confeccionada en poliéster reciclado. Diseño versátil perfecto para el día a día con el icónico logo de tres rayas.',
        categoria=categorias['ropa'],
        marca=marcas['adidas'],
        precio=Decimal('89.99'),
        precio_oferta=Decimal('69.99'),
        stock=60,
        sku='ADI-JKT-ORG-M',
        peso=Decimal('0.45'),
        disponible=True,
        destacado=False,
        activo=True
    ))
    
    productos.append(Producto.objects.create(
        nombre='Vestido Zara Elegante',
        slug='vestido-zara-elegante',
        descripcion_corta='Vestido midi para ocasiones especiales',
        descripcion='Vestido midi de corte elegante, perfecto para eventos. Tejido fluido con acabados de calidad y diseño contemporáneo.',
        categoria=categorias['ropa'],
        marca=marcas['zara'],
        precio=Decimal('59.99'),
        stock=40,
        sku='ZARA-VST-ELG-M',
        peso=Decimal('0.35'),
        disponible=True,
        destacado=False,
        activo=True
    ))
    
    # Productos de Hogar
    productos.append(Producto.objects.create(
        nombre='Escritorio IKEA Bekant',
        slug='escritorio-ikea-bekant',
        descripcion_corta='Escritorio ajustable para oficina en casa',
        descripcion='Escritorio de altura regulable con superficie de 160x80 cm. Estructura robusta y sistema eléctrico de ajuste. Perfecto para trabajar desde casa.',
        categoria=categorias['hogar'],
        marca=marcas['ikea'],
        precio=Decimal('449.99'),
        stock=20,
        sku='IKEA-BKNT-160',
        peso=Decimal('45.5'),
        dimensiones='160 x 80 x 65-125',
        disponible=True,
        destacado=True,
        activo=True
    ))
    
    productos.append(Producto.objects.create(
        nombre='Lámpara LED Inteligente',
        slug='lampara-led-inteligente',
        descripcion_corta='Control por app y cambio de color',
        descripcion='Lámpara LED smart con 16 millones de colores. Compatible con Alexa y Google Home. Control de brillo y temperatura de color vía app.',
        categoria=categorias['hogar'],
        marca=None,
        precio=Decimal('39.99'),
        precio_oferta=Decimal('29.99'),
        stock=150,
        sku='LED-SMART-001',
        peso=Decimal('0.28'),
        disponible=True,
        destacado=False,
        activo=True
    ))
    
    # Productos de Deportes
    productos.append(Producto.objects.create(
        nombre='Bicicleta de Montaña',
        slug='bicicleta-montana-pro',
        descripcion_corta='MTB profesional 29 pulgadas',
        descripcion='Bicicleta de montaña con cuadro de aluminio, suspensión delantera de 120mm, frenos de disco hidráulicos y 21 velocidades. Rodado 29".',
        categoria=categorias['deportes'],
        marca=None,
        precio=Decimal('599.99'),
        stock=15,
        sku='MTB-PRO-29-BLK',
        peso=Decimal('13.5'),
        dimensiones='180 x 95 x 70',
        disponible=True,
        destacado=True,
        activo=True
    ))
    
    productos.append(Producto.objects.create(
        nombre='Mancuernas Ajustables 20kg',
        slug='mancuernas-ajustables-20kg',
        descripcion_corta='Set de mancuernas para entrenamiento en casa',
        descripcion='Par de mancuernas ajustables de 2.5kg a 20kg cada una. Incluye soporte y sistema de ajuste rápido. Ideales para gimnasio en casa.',
        categoria=categorias['deportes'],
        marca=None,
        precio=Decimal('149.99'),
        stock=35,
        sku='DUMBBELL-ADJ-20',
        peso=Decimal('42.0'),
        disponible=True,
        destacado=False,
        activo=True
    ))
    
    # Productos de Libros
    productos.append(Producto.objects.create(
        nombre='Cien Años de Soledad',
        slug='cien-anos-soledad',
        descripcion_corta='Obra maestra de Gabriel García Márquez',
        descripcion='La novela más emblemática de la literatura latinoamericana. Edición especial con prólogo e ilustraciones. Pasta dura.',
        categoria=categorias['libros'],
        marca=None,
        precio=Decimal('24.99'),
        stock=80,
        sku='BOOK-100ANOS-ESP',
        peso=Decimal('0.65'),
        dimensiones='23 x 15 x 3',
        disponible=True,
        destacado=False,
        activo=True
    ))
    
    productos.append(Producto.objects.create(
        nombre='Sapiens: De Animales a Dioses',
        slug='sapiens-yuval-harari',
        descripcion_corta='Bestseller de Yuval Noah Harari',
        descripcion='Una fascinante exploración de la historia de la humanidad desde la Edad de Piedra hasta la actualidad. Bestseller internacional.',
        categoria=categorias['libros'],
        marca=None,
        precio=Decimal('19.99'),
        precio_oferta=Decimal('16.99'),
        stock=120,
        sku='BOOK-SAPIENS-ESP',
        peso=Decimal('0.55'),
        dimensiones='23 x 15 x 2.5',
        disponible=True,
        destacado=False,
        activo=True
    ))
    
    print(f"✅ {len(productos)} productos creados")
    
    # Crear algunos datos de media para productos destacados
    print("\n🖼️ Creando media de ejemplo...")
    media_count = 0
    
    for producto in productos[:5]:  # Solo para los primeros 5 productos
        # Crear 2-3 "imágenes" de ejemplo
        for i in range(2):
            MediaProducto.objects.create(
                producto=producto,
                tipo='imagen',
                titulo=f'Imagen {i+1} de {producto.nombre}',
                descripcion=f'Vista {i+1} del producto',
                alt_text=f'{producto.nombre} - vista {i+1}',
                es_principal=(i == 0),
                orden=i,
                activo=True
            )
            media_count += 1
    
    print(f"✅ {media_count} elementos de media creados (sin archivos reales)")
    
    # Resumen
    print("\n" + "="*50)
    print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
    print("="*50)
    print(f"📁 Categorías: {Categoria.objects.count()}")
    print(f"🏷️ Marcas: {Marca.objects.count()}")
    print(f"📦 Productos: {Producto.objects.count()}")
    print(f"🖼️ Media: {MediaProducto.objects.count()}")
    print("\n💡 Ahora puedes:")
    print("   1. Ver los productos en el admin: http://localhost:8000/admin/")
    print("   2. Acceder a la tienda: http://localhost:8000/")
    print("="*50)

if __name__ == '__main__':
    crear_datos_prueba()
