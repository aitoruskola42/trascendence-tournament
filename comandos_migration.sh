#!/bin/bash

#limpiar temporales
sudo find . -name "*.pyc" -delete

# Ejecutar migraciones

docker exec -it tournament_api python manage.py makemigrations 
docker exec -it tournament_api python manage.py migrate

