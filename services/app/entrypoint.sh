#!/bin/sh

if [ "$DATABASE" = "my_db" ]
then
    echo "Waiting for my_db..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$FLASK_ENV" = "development" ]
then
    echo "Creating the database tables..."
    python manage.py create_db
    python manage.py init_load_db
    echo "Tables created and loaded with data"
fi

exec "$@"