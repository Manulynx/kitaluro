web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn kitaluro.wsgi:application --bind 0.0.0.0:$PORT
