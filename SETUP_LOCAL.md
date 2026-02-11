# 🛠️ Guía de Instalación Local - Kitaluro

Esta guía te ayudará a configurar el proyecto Kitaluro en tu máquina local para desarrollo.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

### 1. **Python 3.10 o superior**

- Descargar desde: https://www.python.org/downloads/
- Durante la instalación, marca la opción **"Add Python to PATH"**
- Verificar instalación:
  ```powershell
  python --version
  ```

### 2. **Docker Desktop** (para PostgreSQL)

- Descargar desde: https://www.docker.com/products/docker-desktop/
- Instalar y asegurarse de que Docker esté corriendo
- Verificar instalación:
  ```powershell
  docker --version
  ```

### 3. **Git** (para clonar el repositorio)

- Descargar desde: https://git-scm.com/downloads

---

## 🚀 Instalación Paso a Paso

### Paso 1: Clonar el Repositorio

```powershell
git clone <URL_DEL_REPOSITORIO>
cd Kitaluro/kitaluro
```

### Paso 2: Instalar Dependencias de Python

```powershell
pip install -r requirements.txt
```

**Dependencias principales:**

- Django 5.2.7
- psycopg2-binary (driver PostgreSQL)
- python-dotenv (variables de entorno)
- dj-database-url
- whitenoise (archivos estáticos)
- Pillow (procesamiento de imágenes)

**Nota:** Cloudinary y Redis se instalan pero solo se usan en producción.

### Paso 3: Configurar PostgreSQL con Docker

#### 3.1 Crear y ejecutar el contenedor PostgreSQL

```powershell
docker run --name postgres_kitaluro -e POSTGRES_PASSWORD=Kitaluro2026! -d -p 54320:5432 postgres:16
```

**Parámetros:**

- `--name postgres_kitaluro`: Nombre del contenedor
- `-e POSTGRES_PASSWORD=Kitaluro2026!`: Contraseña del usuario postgres
- `-p 54320:5432`: Mapea el puerto 54320 de tu PC al puerto 5432 del contenedor
- `postgres:16`: Imagen de PostgreSQL versión 16

#### 3.2 Verificar que el contenedor esté corriendo

```powershell
docker ps
```

Deberías ver algo como:

```
CONTAINER ID   IMAGE         PORTS                      NAMES
feba2560eacf   postgres:16   0.0.0.0:54320->5432/tcp    postgres_kitaluro
```

#### 3.3 Crear la base de datos

```powershell
docker exec -it postgres_kitaluro psql -U postgres -c "CREATE DATABASE kitaluro_local;"
```

### Paso 4: Configurar Variables de Entorno

Crea un archivo `.env` en la carpeta `kitaluro/` (al mismo nivel que `manage.py`) con el siguiente contenido:

```env
# ========================================
# CONFIGURACIÓN LOCAL - Django + PostgreSQL (Docker)
# ========================================

# Django
DEBUG=True
SECRET_KEY=django-insecure-lmh&7!%ru4a!t$l)an3%t14#9%udo=m*pru)qc%yw$kzmj@j29

# PostgreSQL Local (Docker en puerto 54320)
# Usuario: postgres | Contraseña: Kitaluro2026! | Base de datos: kitaluro_local
DATABASE_URL=postgresql://postgres:Kitaluro2026!@localhost:54320/kitaluro_local
```

### Paso 5: Ejecutar Migraciones

```powershell
python manage.py migrate
```

Este comando creará todas las tablas necesarias en la base de datos PostgreSQL.

### Paso 6: Crear un Superusuario

```powershell
python manage.py createsuperuser
```

Te pedirá:

- **Username**: Tu nombre de usuario (ej: `admin`)
- **Email**: Tu correo (opcional)
- **Password**: Tu contraseña (se pedirá dos veces)

### Paso 7: Ejecutar el Servidor de Desarrollo

```powershell
python manage.py runserver
```

El servidor estará disponible en: **http://127.0.0.1:8000/**

---

## 🔑 Acceso al Panel de Administración

- **URL**: http://127.0.0.1:8000/productos/admin/login/
- **Usuario**: El que creaste en el Paso 6
- **Contraseña**: La que configuraste en el Paso 6

---

## 🐳 Comandos Útiles de Docker

### Iniciar el contenedor PostgreSQL (si está detenido)

```powershell
docker start postgres_kitaluro
```

### Detener el contenedor

```powershell
docker stop postgres_kitaluro
```

### Ver logs del contenedor

```powershell
docker logs postgres_kitaluro
```

### Acceder a la consola PostgreSQL (psql)

```powershell
docker exec -it postgres_kitaluro psql -U postgres -d kitaluro_local
```

### Eliminar el contenedor (si necesitas recrearlo)

```powershell
docker stop postgres_kitaluro
docker rm postgres_kitaluro
```

---

## 🔧 Solución de Problemas

### Error: "docker: command not found"

- Asegúrate de que Docker Desktop esté instalado y corriendo
- Reinicia tu terminal después de instalar Docker

### Error: "port is already allocated"

- El puerto ya está en uso. Cambia el puerto en el comando docker run:
  ```powershell
  docker run --name postgres_kitaluro -e POSTGRES_PASSWORD=Kitaluro2026! -d -p 54321:5432 postgres:16
  ```
- Actualiza el `DATABASE_URL` en `.env` al nuevo puerto

### Error: "No module named 'X'"

- Asegúrate de haber instalado todas las dependencias:
  ```powershell
  pip install -r requirements.txt
  ```

### Error: "connection to server failed: SSL required"

- Esto ya está solucionado en `settings.py`. Asegúrate de que `DEBUG=True` en tu `.env`

---

## 📁 Estructura del Proyecto

```
kitaluro/
├── .env                          # Variables de entorno (NO subir a Git)
├── manage.py                     # Script de gestión de Django
├── requirements.txt              # Dependencias Python
├── db.sqlite3                    # Base de datos SQLite (solo para respaldo)
├── kitaluro/                     # Configuración principal
│   ├── settings.py               # Configuración de Django
│   ├── urls.py                   # URLs principales
│   └── templates/                # Plantillas HTML
├── productos/                    # App de productos
│   ├── models.py                 # Modelos de datos
│   ├── views.py                  # Vistas
│   └── admin.py                  # Configuración del admin
├── static/                       # Archivos estáticos (CSS, JS, imágenes)
└── media/                        # Archivos subidos (en local)
```

---

## 🚀 Despliegue en Producción (Railway)

Este proyecto está configurado para desplegarse automáticamente en Railway. La configuración de producción:

- Usa PostgreSQL con SSL (proporcionado por Railway)
- Los archivos media se suben a **Cloudinary**
- Los archivos estáticos se sirven con **WhiteNoise**
- Usa **Gunicorn** como servidor WSGI

**Variables de entorno en Railway:**

- `DATABASE_URL`: Proporcionada automáticamente por Railway
- `SECRET_KEY`: Clave secreta única
- `DEBUG=False`
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
- `REDIS_URL`: Para caché (opcional)

---

## 📝 Notas Adicionales

### Archivo .env

- **NUNCA** subas el archivo `.env` a Git
- Ya está incluido en `.gitignore`
- Cada desarrollador debe crear su propio `.env` local

### Base de Datos

- **Local**: PostgreSQL en Docker (puerto 54320)
- **Producción**: PostgreSQL en Railway (con SSL)

### Archivos Media

- **Local**: Se guardan en la carpeta `media/` del proyecto (almacenamiento local)
- **Producción**: Se suben a Cloudinary automáticamente

### Cache y Sesiones

- **Local**: Se usa cache en base de datos PostgreSQL y sesiones en BD
- **Producción**: Se usa Redis para cache y sesiones (mejor rendimiento)

---

## 🆘 Soporte

Si tienes problemas con la configuración, verifica:

1. ✅ Docker Desktop está corriendo
2. ✅ El contenedor PostgreSQL está activo (`docker ps`)
3. ✅ El archivo `.env` existe y tiene las variables correctas
4. ✅ Todas las dependencias están instaladas
5. ✅ Las migraciones se ejecutaron correctamente

---

**¡Listo para desarrollar! 🎉**
