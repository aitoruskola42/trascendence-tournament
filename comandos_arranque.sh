#!/bin/bash


docker cp create_dummy_data.py tournament_api:/usr/src/app/

# Verificar que el archivo se copió correctamente
docker exec tournament_api ls /usr/src/app

# Ejecutar el script
docker exec -it tournament_api python /usr/src/app/create_dummy_data.py

# Ejecutar migraciones
docker exec -it tournament_api python manage.py makemigrations 
docker exec -it tournament_api python manage.py migrate