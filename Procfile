release: python manage.py migrate --noinput
web: python manage.py collectstatic --noinput && gunicorn kitaluro.wsgi --bind 0.0.0.0:$PORT