# 🔐 Sistema de Autenticación - Área de Administración

## ✅ Implementación Profesional con Django Superuser

Se ha implementado un sistema de autenticación profesional utilizando el sistema nativo de Django con superusuarios.

## 🔑 Acceso al Sistema

**URL de Login:** `/productos/admin/login/`

### Crear un Superusuario

Para acceder al área de administración, primero debes crear un superusuario:

```bash
python manage.py createsuperuser
```

Te pedirá:

- **Username**: Tu nombre de usuario
- **Email**: Tu correo electrónico (opcional)
- **Password**: Tu contraseña (se pedirá dos veces para confirmar)

Ejemplo:

```
Username: admin
Email address: admin@kitaluro.com
Password: **********
Password (again): **********
Superuser created successfully.
```

## 🛡️ Características Implementadas

### 1. **Autenticación con Django**

- Usa el sistema de autenticación nativo de Django
- Verificación de credenciales mediante `authenticate()`
- Login seguro con `login()` de Django
- Solo permite acceso a usuarios con `is_superuser=True`

### 2. **Protección de Rutas**

Todas las vistas de administración están protegidas con el decorador `@admin_required`:

- ✅ Verifica que el usuario esté autenticado (`request.user.is_authenticated`)
- ✅ Verifica que sea superusuario (`request.user.is_superuser`)
- ✅ Redirige al login si no cumple los requisitos

### 3. **Navbar Condicional**

- El enlace "ADMIN" **solo se muestra** si el usuario es un superusuario autenticado
- Funciona tanto en el menú desktop como en el menú móvil
- Basado en `request.user.is_authenticated and request.user.is_superuser`

### 4. **Gestión de Sesiones**

- Usa el sistema de sesiones de Django
- Mantiene el estado de autenticación de forma segura
- Compatible con todos los settings de sesión de Django

### 5. **Logout Seguro**

- Botón de "Cerrar Sesión" en el área de administración
- Usa `logout()` de Django para cerrar sesión de forma segura
- Redirige al home con mensaje de confirmación

## 📂 Archivos Modificados

### Archivos Modificados:

1. `productos/views.py` - Sistema de autenticación con Django superuser
2. `kitaluro/templates/base.html` - Navbar condicional con `request.user.is_superuser`
3. `productos/templates/admin_lista_productos.html` - Botón de cerrar sesión

## 🚀 Cómo Usar

### 1. Crear un Superusuario (Primera vez):

```bash
python manage.py createsuperuser
```

### 2. Acceder al Área de Administración:

1. **Navega a la URL de login:**

   ```
   http://localhost:8000/productos/admin/login/
   ```

2. **Ingresa tus credenciales de superusuario:**

   - Usuario: El username que creaste
   - Contraseña: La contraseña que estableciste

3. **Accede al panel de administración:**

   - Serás redirigido automáticamente a `/productos/admin/`
   - El enlace "ADMIN" aparecerá en el navbar

4. **Cerrar sesión:**
   - Haz clic en el botón "Cerrar Sesión" en el área de admin
   - O navega a `/productos/admin/logout/`

### 3. Intentar Acceder Sin Autenticación:

Si intentas acceder directamente a cualquier URL de admin sin estar autenticado:

```
http://localhost:8000/productos/admin/
http://localhost:8000/productos/admin/nuevo/
http://localhost:8000/productos/admin/taxonomias/
```

Serás redirigido automáticamente a la página de login con un mensaje de error.

## 🔧 Gestión de Usuarios

### Crear Superusuarios Adicionales:

```bash
python manage.py createsuperuser
```

### Promover un Usuario Existente a Superuser (Django Shell):

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
user = User.objects.get(username='nombre_usuario')
user.is_superuser = True
user.is_staff = True
user.save()
```

### Cambiar Contraseña de un Superusuario:

```bash
python manage.py changepassword nombre_usuario
```

### Ver Todos los Superusuarios (Django Shell):

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
superusers = User.objects.filter(is_superuser=True)
for user in superusers:
    print(f"Username: {user.username}, Email: {user.email}")
```

## 🎨 Diseño del Login

El template de login incluye:

- ✨ Gradiente oscuro profesional
- 🔒 Icono de candado animado
- 💎 Efecto glass morphism en la tarjeta
- 🎯 Animaciones suaves al escribir
- 📱 Diseño completamente responsive
- 🌙 Compatible con modo oscuro
- 🔐 Badge de "Conexión segura"

## 📝 Ventajas del Sistema

- ✅ **Seguridad profesional**: Usa el sistema probado de Django
- ✅ **Contraseñas hasheadas**: Las contraseñas se almacenan de forma segura con PBKDF2
- ✅ **Múltiples superusuarios**: Puedes tener varios administradores
- ✅ **Fácil gestión**: Comandos de Django para gestionar usuarios
- ✅ **Escalable**: Compatible con autenticación de dos factores y otros plugins
- ✅ **Sin credenciales hardcodeadas**: No hay contraseñas en el código
- ✅ **Producción lista**: Sistema listo para producción

## 🔄 Flujo de Autenticación

```
Usuario intenta acceder a /productos/admin/
    ↓
¿Está autenticado? (request.user.is_authenticated)
    ↓
NO → Redirigir a /productos/admin/login/
    ↓
Usuario ingresa credenciales
    ↓
Django valida con authenticate()
    ↓
¿Usuario existe y contraseña correcta?
    ↓
SÍ → ¿Es superusuario? (is_superuser=True)
    ↓
SÍ → login(request, user) + Redirigir a /productos/admin/
    ↓
Usuario puede navegar por todas las áreas de admin
    ↓
Usuario hace clic en "Cerrar Sesión"
    ↓
logout(request) + Redirigir a home
```

## 🔒 Seguridad

### Características de Seguridad:

- ✅ Contraseñas hasheadas con PBKDF2-SHA256
- ✅ Protección CSRF en formularios
- ✅ Sesiones seguras de Django
- ✅ Verificación de superusuario en cada request
- ✅ Mensajes informativos sin exponer datos sensibles
- ✅ Logout completo con limpieza de sesión

### Recomendaciones para Producción:

- ⚠️ Usa HTTPS siempre en producción
- ⚠️ Configura `SESSION_COOKIE_SECURE = True` en settings.py
- ⚠️ Considera implementar rate limiting para login
- ⚠️ Configura `CSRF_COOKIE_SECURE = True` en producción
- ⚠️ Usa contraseñas fuertes para superusuarios
- ⚠️ Considera autenticación de dos factores (2FA) con django-otp

## ✨ Características Adicionales

- El enlace "ADMIN" en el navbar **solo aparece cuando estás autenticado como superusuario**
- Los usuarios no autenticados no pueden ver que existe un área de administración
- Perfecto para mantener el acceso de administración discreto y seguro
- Compatible con el admin nativo de Django (`/admin/`)

## 🆚 Diferencias con el Sistema Anterior

| Característica     | Sistema Anterior          | Sistema Actual           |
| ------------------ | ------------------------- | ------------------------ |
| Autenticación      | Credenciales hardcodeadas | Django authenticate()    |
| Almacenamiento     | Variables en código       | Base de datos            |
| Seguridad          | Contraseña en texto plano | Contraseñas hasheadas    |
| Múltiples usuarios | No                        | Sí, ilimitados           |
| Gestión            | Manual en código          | Comandos de Django       |
| Producción         | No recomendado            | ✅ Listo para producción |

---

**Desarrollado con ❤️ para Kitaluro - Sistema Profesional de Autenticación**
