"""
Script para crear un superusuario adicional en Railway
Configura estas variables de entorno en Railway:
- ADMIN2_USERNAME
- ADMIN2_EMAIL
- ADMIN2_PASSWORD
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kitaluro.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Puedes crear múltiples superusuarios con diferentes prefijos
SUPERUSERS = [
    {
        "username": os.getenv("ADMIN2_USERNAME"),
        "email": os.getenv("ADMIN2_EMAIL"),
        "password": os.getenv("ADMIN2_PASSWORD"),
    },
    # Puedes agregar más aquí con ADMIN3_, ADMIN4_, etc.
]

for admin_data in SUPERUSERS:
    username = admin_data.get("username")
    email = admin_data.get("email")
    password = admin_data.get("password")
    
    if not username or not password:
        continue  # Salta si no están las variables
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email or f"{username}@kitaluro.com"}
    )
    
    if created:
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✅ Superusuario creado: {username}")
    else:
        print(f"ℹ️ Superusuario ya existe: {username}")

print("\n✅ Proceso completado")
