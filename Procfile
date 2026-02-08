web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn kitaluro.wsgi --bind 0.0.0.0:$PORT --workers 3 --timeout 120
