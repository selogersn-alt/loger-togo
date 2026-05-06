#!/bin/sh

# Attendre que la base de données soit prête (optionnel mais recommandé)
# sleep 5

echo "--> Application des migrations..."
python manage.py migrate --noinput

echo "--> Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "--> Compilation des traductions..."
python manage.py compilemessages

echo "--> Démarrage du serveur Gunicorn..."
gunicorn logertogo.wsgi:application --bind 0.0.0.0:8000 --workers 3
