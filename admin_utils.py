"""
Script de utilidad para gestionar superusuarios de Kitaluro
Ejecutar desde la raíz del proyecto: python manage.py shell < admin_utils.py
"""

from django.contrib.auth.models import User


def list_superusers():
    """Listar todos los superusuarios"""
    superusers = User.objects.filter(is_superuser=True)
    print("\n=== SUPERUSUARIOS DE KITALURO ===\n")
    if superusers.exists():
        for user in superusers:
            print(f"Username: {user.username}")
            print(f"Email: {user.email or 'No especificado'}")
            print(f"Nombre: {user.get_full_name() or 'No especificado'}")
            print(f"Activo: {'Sí' if user.is_active else 'No'}")
            print(f"Staff: {'Sí' if user.is_staff else 'No'}")
            print(f"Último login: {user.last_login or 'Nunca'}")
            print("-" * 50)
    else:
        print("No hay superusuarios registrados.")
        print("\nPara crear uno, ejecuta:")
        print("  python manage.py createsuperuser")


def create_superuser_programmatic(username, email, password):
    """
    Crear un superusuario programáticamente
    SOLO USAR EN DESARROLLO - No usar en producción
    """
    if User.objects.filter(username=username).exists():
        print(f"❌ El usuario '{username}' ya existe.")
        return None
    
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"✅ Superusuario '{username}' creado exitosamente.")
    return user


def promote_to_superuser(username):
    """Promover un usuario existente a superusuario"""
    try:
        user = User.objects.get(username=username)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"✅ Usuario '{username}' promovido a superusuario.")
    except User.DoesNotExist:
        print(f"❌ El usuario '{username}' no existe.")


def demote_from_superuser(username):
    """Quitar privilegios de superusuario"""
    try:
        user = User.objects.get(username=username)
        user.is_superuser = False
        user.save()
        print(f"✅ Privilegios de superusuario removidos de '{username}'.")
    except User.DoesNotExist:
        print(f"❌ El usuario '{username}' no existe.")


def deactivate_user(username):
    """Desactivar un usuario"""
    try:
        user = User.objects.get(username=username)
        user.is_active = False
        user.save()
        print(f"✅ Usuario '{username}' desactivado.")
    except User.DoesNotExist:
        print(f"❌ El usuario '{username}' no existe.")


def activate_user(username):
    """Activar un usuario"""
    try:
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        print(f"✅ Usuario '{username}' activado.")
    except User.DoesNotExist:
        print(f"❌ El usuario '{username}' no existe.")


# Ejecutar al cargar el script
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🔐 UTILIDADES DE ADMINISTRACIÓN - KITALURO")
    print("="*50)
    
    list_superusers()
    
    print("\n\n=== FUNCIONES DISPONIBLES ===\n")
    print("list_superusers() - Listar todos los superusuarios")
    print("create_superuser_programmatic(username, email, password) - Crear superusuario")
    print("promote_to_superuser(username) - Promover usuario a superuser")
    print("demote_from_superuser(username) - Remover privilegios de superuser")
    print("activate_user(username) - Activar usuario")
    print("deactivate_user(username) - Desactivar usuario")
    print("\nEjemplo de uso:")
    print("  promote_to_superuser('juan')")
    print("\n" + "="*50 + "\n")
