#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic --noinput
echo "from accounts.models import User; import os; User.objects.create_superuser(
  os.environ.get('DJ_ADMIN_USERNAME'), '', os.environ.get('DJ_ADMIN_PASSWORD'), last_name='ADMIN', first_name='ADMIN')" | python manage.py shell
gunicorn main.wsgi:application --bind 0.0.0.0:8000

exec "$@"

