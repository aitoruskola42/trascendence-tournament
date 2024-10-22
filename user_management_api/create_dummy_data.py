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

# Función auxiliar para ejecutar SQL
def execute_sql(sql, params=None):
    with connection.cursor() as cursor:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        if sql.strip().upper().startswith('INSERT') and 'RETURNING' in sql.upper():
            return cursor.fetchone()[0]
        elif sql.strip().upper().startswith('SELECT'):
            return cursor.fetchall()

# Lista de nombres para generar jugadores
PLAYER_NAMES = [
    "Juan Pérez", "Ana García", "Carlos Ruiz", "María López", 
    "Pedro Sánchez", "Laura Martínez", "Diego González", "Sofia Rodríguez",
    "Miguel Torres", "Elena Castro"
]

def create_matches():
    # Insertar partidas individuales
    match_sql = """
    INSERT INTO api_match (
        match_type, tournament_id, player1_id, player2_id,
        player1_display_name, player2_display_name,
        player1_score, player2_score, winner_id, date
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Generar partidas individuales
    for _ in range(10):
        player1, player2 = random.sample(range(1, len(PLAYER_NAMES) + 1), 2)
        player1_score = random.randint(0, 2)
        player2_score = random.randint(0, 2)
        while player1_score == player2_score:
            player1_score = random.randint(0, 2)
            player2_score = random.randint(0, 2)
        winner_id = player1 if player1_score > player2_score else player2
        random_date = datetime.now(pytz.UTC) - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23)
        )

        execute_sql(match_sql, (
            'INDIVIDUAL',
            0,
            player1,
            player2,
            PLAYER_NAMES[player1-1],
            PLAYER_NAMES[player2-1],
            player1_score,
            player2_score,
            winner_id,
            random_date
        ))

    # Generar torneos
    for tournament_id in range(3, 18):  # 15 torneos nuevos (empezamos en 3 ya que ya existen 2)
        players = random.sample(range(1, len(PLAYER_NAMES) + 1), 4)
        # Generamos fechas más distribuidas para tener un histórico más realista
        tournament_date = datetime.now(pytz.UTC) - timedelta(
            days=random.randint(0, 180),  # Aumentamos el rango a 6 meses para más variedad
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        # Semifinales
        semifinal_winners = []
        for i in range(0, 4, 2):
            player1, player2 = players[i:i+2]
            player1_score = random.randint(0, 2)
            player2_score = random.randint(0, 2)
            while player1_score == player2_score:
                player1_score = random.randint(0, 2)
                player2_score = random.randint(0, 2)
            winner = player1 if player1_score > player2_score else player2
            semifinal_winners.append(winner)

            execute_sql(match_sql, (
                'SEMIFINAL',
                tournament_id,
                player1,
                player2,
                PLAYER_NAMES[player1-1],
                PLAYER_NAMES[player2-1],
                player1_score,
                player2_score,
                winner,
                tournament_date + timedelta(hours=i)
            ))

        # Final
        finalist1, finalist2 = semifinal_winners
        player1_score = random.randint(0, 2)
        player2_score = random.randint(0, 2)
        while player1_score == player2_score:
            player1_score = random.randint(0, 2)
            player2_score = random.randint(0, 2)
        winner = finalist1 if player1_score > player2_score else finalist2

        execute_sql(match_sql, (
            'FINAL',
            tournament_id,
            finalist1,
            finalist2,
            PLAYER_NAMES[finalist1-1],
            PLAYER_NAMES[finalist2-1],
            player1_score,
            player2_score,
            winner,
            tournament_date + timedelta(hours=4)
        ))

if __name__ == "__main__":
    create_matches()