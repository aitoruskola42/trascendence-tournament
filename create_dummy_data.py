import hashlib
import os
import django
import sys
import random
from datetime import datetime, timedelta
import pytz

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_management_api.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from api.models import ApiUser, Tournament, Participation, Match2, Match4

# Función auxiliar para ejecutar SQL
def execute_sql(sql, params=None):
    with connection.cursor() as cursor:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        if sql.strip().upper().startswith('INSERT') and 'RETURNING' in sql.upper():
            return cursor.fetchone()[0]  # Retorna el ID del nuevo registro
        elif sql.strip().upper().startswith('SELECT'):
            return cursor.fetchall()

def create_users(num_users=50):
    users_sql = """
    INSERT INTO auth_user (username, email, password, first_name, last_name, is_active, date_joined, is_superuser, is_staff)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    api_users_sql = """
    INSERT INTO api_apiuser (user_id, display_name, avatar_image, friends, friends_wait, friends_request, friends_blocked, user_42, two_factor_enabled, two_factor_configured)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Obtener los IDs de usuario existentes en auth_user
    existing_users = execute_sql("SELECT id FROM auth_user")
    existing_user_ids = [user[0] for user in existing_users]
    
    created_users = []
    for i in range(1, num_users + 1):
        username = f"user{i}"
        email = f"user{i}@example.com"
        password = hashlib.sha256(f"password{i}".encode()).hexdigest()
        first_name = f"FirstName{i}"
        last_name = f"LastName{i}"
        is_active = True
        date_joined = datetime.now(pytz.UTC)
        is_superuser = False
        is_staff = False
        
        if i not in existing_user_ids:
            user_id = execute_sql(users_sql, (username, email, password, first_name, last_name, is_active, date_joined, is_superuser, is_staff))
        else:
            user_id = i
        
        created_users.append(user_id)
        
        # Verificar si el usuario ya existe en api_apiuser
        api_user_exists = execute_sql("SELECT COUNT(*) FROM api_apiuser WHERE user_id = %s", (user_id,))[0][0]
        
        if api_user_exists == 0:
            display_name = f"User {i}"
            avatar_image = "avatars/default.jpg"
            friends = ",".join(str(random.randint(1, num_users)) for _ in range(5))
            friends_wait = ",".join(str(random.randint(1, num_users)) for _ in range(3))
            friends_request = ",".join(str(random.randint(1, num_users)) for _ in range(3))
            friends_blocked = ",".join(str(random.randint(1, num_users)) for _ in range(2))
            user_42 = False
            two_factor_enabled = random.choice([True, False])
            two_factor_configured = False
            
            execute_sql(api_users_sql, (user_id, display_name, avatar_image, friends, friends_wait, friends_request, friends_blocked, user_42, two_factor_enabled, two_factor_configured))

    print(f"Created or updated {num_users} users")
    print(f"User IDs: {created_users}")


def create_tournaments(num_tournaments=50):
    tournaments_sql = """
    INSERT INTO api_tournament (name, start_date, status, tournament_type, creator, max_participants)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    
    
    start_date = datetime.now(pytz.UTC) + timedelta(days=random.randint(1, 30))

    execute_sql(tournaments_sql, ('Torneo Aitor 1', start_date , 'REGISTRATION',  'FOUR_PLAYER', 1, 4))
    execute_sql(tournaments_sql, ('Torneo Aitor 2', start_date , 'REGISTRATION', 'TWO_PLAYER', 1, 2))


    execute_sql(tournaments_sql, ('Torneo Iker 1', start_date , 'REGISTRATION', 'FOUR_PLAYER', 2, 4))
    execute_sql(tournaments_sql, ('Torneo Iker 2', start_date , 'REGISTRATION', 'TWO_PLAYER', 2, 2))

    execute_sql(tournaments_sql, ('Torneo Alejandro 1', start_date , 'REGISTRATION', 'FOUR_PLAYER', 3, 4))
    execute_sql(tournaments_sql, ('Torneo Alejandro 2', start_date , 'REGISTRATION', 'TWO_PLAYER', 3, 2))

    execute_sql(tournaments_sql, ('Torneo Goiko 1', start_date , 'REGISTRATION', 'FOUR_PLAYER', 4, 4))
    execute_sql(tournaments_sql, ('Torneo Goko 2', start_date , 'REGISTRATION', 'TWO_PLAYER', 4, 2))


    print(f"Created tournaments")
""" 
    for i in range(1, num_tournaments + 1):
        name = f"Tournament {i}"
        start_date = datetime.now(pytz.UTC) + timedelta(days=random.randint(1, 30))
        status = random.choice(statuses)
        tournament_type = random.choice(types)
        creator = random.randint(1, 50)  # Asumiendo que hay 50 usuarios
        max_participants = 2 if tournament_type == 'TWO_PLAYER' else 4
        
        execute_sql(tournaments_sql, (name, start_date, status, tournament_type, creator, max_participants))
"""
 

def create_participations():
    participations_sql = """
    INSERT INTO api_participation (user_id, tournament_id, score, display_name)
    VALUES (%s, %s, %s, %s)
    """


    score = random.randint(0, 5)
    execute_sql(participations_sql, (3, 1, score, "goiko display"))
    score = random.randint(0, 5)
    execute_sql(participations_sql, (1, 1, score, "ait or displa y"))
    score = random.randint(0, 5)
    execute_sql(participations_sql, (4, 1, score, "alejandro display"))
    score = random.randint(0, 5)
    execute_sql(participations_sql, (1, 2, score, "alejandro display"))
    score = random.randint(0, 5)
    execute_sql(participations_sql, (2, 1, score, "Goiko display 2"))
    score = random.randint(0, 5)
    execute_sql(participations_sql, (1, 3, score, "user raro dis play"))
    score = random.randint(0, 5)
    execute_sql(participations_sql, (3, 3, score, "user raro displa y"))
    score = random.randint(0, 5)
    execute_sql(participations_sql, (4, 4, score, "user ra ro display"))
    score = random.randint(0, 5)
    execute_sql(participations_sql, (5, 5, score, "us er ra ro display"))
    score = random.randint(0, 5)
    execute_sql(participations_sql, (6, 6, score, "us er ra ro display"))

    score = random.randint(0, 5)
    execute_sql(participations_sql, (5, 2, score, "us er ra ro display"))
    score = random.randint(0, 5)
    execute_sql(participations_sql, (6, 4, score, "us er ra ro display"))

    score = random.randint(0, 5)
    execute_sql(participations_sql, (7, 4, score, "us er ra ro display"))
    score = random.randint(0, 5)
    execute_sql(participations_sql, (8, 4, score, "us er ra ro display"))




"""    
    tournaments = execute_sql("SELECT id, tournament_type, max_participants FROM api_tournament")
    all_users = execute_sql("SELECT user_id, display_name FROM api_apiuser")
    user_dict = {user[0]: user[1] for user in all_users}



    for tournament in tournaments:
        tournament_id, tournament_type, max_participants = tournament
        max_participants = int(max_participants)  # Asegurarse de que es un entero
        
        if len(user_dict) < max_participants:
            print(f"No hay suficientes usuarios para el torneo {tournament_id}. Se necesitan {max_participants}, hay {len(user_dict)}")
            continue
        
        participants = random.sample(list(user_dict.keys()), max_participants)
        
        for user_id in participants:
            score = random.randint(0, 15)
            display_name = user_dict.get(user_id)
            
            if display_name is None:
                print(f"No se encontró el usuario con ID {user_id} en api_apiuser. Saltando este usuario.")
                continue
            
            try:
                execute_sql(participations_sql, (user_id, tournament_id, score, display_name))
            except Exception as e:
                print(f"Error al crear participación para usuario {user_id} en torneo {tournament_id}: {str(e)}")
    
    print("Created participations for all tournaments") """

def create_matches():
    matches2_sql = """
    INSERT INTO api_match2 (tournament_id, player1_id, player2_id, player1_score, player2_score, winner_id, round, "order", date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    matches4_sql = """
    INSERT INTO api_match4 (tournament_id, player1_id, player2_id, player3_id, player4_id, player1_score, player2_score, player3_score, player4_score, winner_id, round, "order", date, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """


    execute_sql(matches2_sql, (2, 1, 2, 10, 11, 2, 1, 1, datetime.now(pytz.UTC)))
    execute_sql(matches2_sql, (4, 2, 3, 10, 11, 1, 1, 1, datetime.now(pytz.UTC)))
        
    execute_sql(matches4_sql, (1, 1, 2, 3, 4, 10, 11, 10, 9, 2, 1, 1, datetime.now(pytz.UTC), 1))
    execute_sql(matches4_sql, (3, 1, 2, 4, 5, 10, 11, 10, 9, 1, 1, 1, datetime.now(pytz.UTC), 1))
          

    
    print("Created matches for all tournaments")

""" 
    for tournament in tournaments:
        tournament_id, tournament_type = tournament
        participants = execute_sql("SELECT id FROM api_participation WHERE tournament_id = %s", (tournament_id,))
        
        if tournament_type == 'TWO_PLAYER':
            player1, player2 = random.sample(participants, 2)
            player1_score = random.randint(0, 11)
            player2_score = random.randint(0, 11)
            winner = player1 if player1_score > player2_score else player2
            
        elif tournament_type == 'FOUR_PLAYER':
            players = random.sample(participants, 4)
            scores = [random.randint(0, 11) for _ in range(4)]
            winner = players[scores.index(max(scores))]
"""
 

def main():
    create_users()
    create_tournaments()
    create_participations()
    create_matches()

if __name__ == "__main__":
    main()