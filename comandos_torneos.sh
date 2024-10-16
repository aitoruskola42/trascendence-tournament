#!/bin/bash

#crear al root
docker exec -it tournament_api bash -c "DJANGO_SUPERUSER_USERNAME=root DJANGO_SUPERUSER_EMAIL=root@example.com DJANGO_SUPERUSER_PASSWORD=root python manage.py createsuperuser --noinput"

create_user_42() {
    curl -X POST http://localhost:60000/api/users/create/ \
         -H "Content-Type: application/json" \
         -d "{
             \"username\": \"$1\",
             \"email\": \"$2\",
             \"password\": \"$3\",
             \"first_name\": \"$4\",
             \"last_name\": \"$5\",
             \"friends\": \"${11}\",
             \"friends_wait\": \"${12}\",
             \"friends_request\": \"${13}\",
             \"friends_blocked\": \"${14}\"

         }"
    echo ""
}

# Crear usuarios
create_user_42 "aitor" "aitor@gmail.com" "aitor" "Aitor" "Completo" 28 "https://ejemplo.com/avatares/completo.png" "online" true "session_id_completo_123456" "2,3" "4,6" "5,9" "10" 
create_user_42 "iker" "iker@gmail.com" "iker" "Iker" "Completo" 29 "https://ejemplo.com/avatares/completo.png" "online" true "session_id_completo_123456" "1,3" "4,8" "6, 12" "8,15" 
create_user_42 "alejandro" "alejandro@gmail.com" "alejandro" "Alejandro" "Completo" 30 "https://ejemplo.com/avatares/completo.png" "offline" true "session_id_completo_123456" "1,2" "2" "9,10" "13,15" 
create_user_42 "goiko" "goiko@gmail.com" "goiko" "Goiko" "Completo" 31 "https://ejemplo.com/avatares/completo.png" "offline" true "session_id_completo_123456" "2,3" "8,3" "6,9" "20,11" 

# Copiar el archivo al directorio correcto
docker cp create_dummy_data.py tournament_api:/usr/src/app/

# Verificar que el archivo se copió correctamente
docker exec tournament_api ls /usr/src/app

# Ejecutar el script
docker exec -it tournament_api python /usr/src/app/create_dummy_data.py

# Ejecutar migraciones
docker exec -it tournament_api python manage.py makemigrations 
docker exec -it tournament_api python manage.py migrate