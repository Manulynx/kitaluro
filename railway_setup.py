import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kitaluro.settings")  # <-- CAMBIA SI TU PROYECTO SE LLAMA DISTINTO
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
EMAIL = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
PASSWORD = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if not PASSWORD:
    raise Exception("Falta DJANGO_SUPERUSER_PASSWORD en Railway Variables")

user, created = User.objects.get_or_create(
    username=USERNAME,
    defaults={"email": EMAIL}
)

if created:
    user.set_password(PASSWORD)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print("✅ Superuser creado:", USERNAME)
else:
    print("ℹ️ Superuser ya existe:", USERNAME)
