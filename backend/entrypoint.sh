#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate
echo "from accounts.models import User; import os; User.objects.create_superuser(
  os.environ.get('DJ_ADMIN_USERNAME'), 'kss@kss.com', os.environ.get('DJ_ADMIN_PASSWORD'), last_name='Курбатов', first_name='Сергей')" | python manage.py shell

exec "$@"

