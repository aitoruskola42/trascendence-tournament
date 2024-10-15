#!/bin/bash

# Ejecutar migraciones
docker exec -it tournament_api python manage.py makemigrations 
docker exec -it tournament_api python manage.py migrate

# Crear superusuario
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

# Función para crear usuario
create_user() {
    local user_id=$1
    local username=$2
    local email=$3
    local password=$4
    local first_name=$5
    local last_name=$6
    local age=$7
    local avatar=$8
    local status=$9
    local is_active=${10}
    local session_id=${11}

    # Generar lista de amigos (12 IDs aleatorios distintos del usuario actual)
    local friends=""
    for i in {1..12}
    do
        local friend_id=$((RANDOM % 50 + 1))
        while [[ $friend_id -eq $user_id || $friends == *"$friend_id"* ]]
        do
            friend_id=$((RANDOM % 50 + 1))
        done
        friends+="$friend_id,"
    done
    friends=${friends%,}  # Eliminar la última coma


    # Generar lista de amigos en espera (12 IDs aleatorios distintos del usuario actual)
    local friends_wait=""
    for i in {1..12}
    do
        local friends_wait_id=$((RANDOM % 50 + 1))
        while [[ $friends_wait_id -eq $user_id || $friends_wait == *"$friends_wait_id"* ]]
        do
            friends_wait_id=$((RANDOM % 50 + 1))
        done
        friends_wait+="$friends_wait_id,"
    done
    friends_wait=${friends_wait%,}  # Eliminar la última coma


    # Generar lista de amigos bloqueados en espera (12 IDs aleatorios distintos del usuario actual)
    local friends_blocked=""
    for i in {1..12}
    do
        local friends_blocked_id=$((RANDOM % 50 + 1))
        while [[ $friends_blocked_id -eq $user_id || $friends_blocked == *"$friends_blocked_id"* ]]
        do
            friends_blocked_id=$((RANDOM % 50 + 1))
        done
        friends_blocked+="$friends_blocked_id,"
    done
    friends_blocked=${friends_blocked%,}  # Eliminar la última coma

    # Generar lista de amigos bloqueados en espera (12 IDs aleatorios distintos del usuario actual)
    local friends_request=""
    for i in {1..12}
    do
        local friends_request_id=$((RANDOM % 50 + 1))
        while [[ $friends_request_id -eq $user_id || $friends_request == *"$friends_request_id"* ]]
        do
            friends_request_id=$((RANDOM % 50 + 1))
        done
        friends_request+="$friends_request_id,"
    done
    friends_request=${friends_request%,}  # Eliminar la última coma


    curl -X POST http://localhost:60000/api/users/create/ \
         -H "Content-Type: application/json" \
         -d "{
             \"username\": \"$username\",
             \"email\": \"$email\",
             \"password\": \"$password\",
             \"first_name\": \"$first_name\",
             \"last_name\": \"$last_name\",
             \"age\": $age,
             \"avatar\": \"$avatar\",
             \"status\": \"$status\",
             \"is_active\": $is_active,
             \"session_id\": \"$session_id\",
             \"friends\": \"$friends\",
             \"friends_wait\": \"$friends_wait\",
             \"friends_blocked\": \"$friends_blocked\",
             \"friends_request\": \"$friends_request\"
         }"
    echo ""
}

# Crear 50 usuarios
for i in {1..50}
do
    username="user$i"
    email="user$i@example.com"
    password="$i"
    first_name="FirstName$i"
    last_name="LastName$i"
    age=$((20 + RANDOM % 40))
    avatar="https://ejemplo.com/avatares/user$i.png"
    status=$( (( RANDOM % 2 )) && echo "online" || echo "offline" )
    is_active="true"
    session_id="session_id_$username"

    create_user $i "$username" "$email" "$password" "$first_name" "$last_name" $age "$avatar" "$status" $is_active "$session_id"
done