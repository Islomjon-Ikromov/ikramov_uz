#!/bin/sh

# chmod +x start.sh

# Create migrations for the 'users', 'index', and 'exam' apps
python manage.py makemigrations index

# Apply migrations
python manage.py migrate

# Collect static files (this gathers static files for production)
python manage.py collectstatic --noinput

# Run the development server
# python manage.py runserver 0.0.0.0:8082

gunicorn core.wsgi:application --bind 0.0.0.0:8082 --workers 1