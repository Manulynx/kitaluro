release: python manage.py migrate --noinput
web: gunicorn kitaluro.wsgi --bind 0.0.0.0:$PORT