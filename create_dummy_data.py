import os
import django
import sys
import traceback
import random
from datetime import timedelta

print("Script started", file=sys.stderr)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_management_api.settings')
django.setup()

print("Django setup complete", file=sys.stderr)

from django.contrib.auth import get_user_model
from django.utils import timezone
from api.models import ApiUser, Tournament, Participation, Match2, Match4

User = get_user_model()

def create_two_player_tournament(users, tournament_number):
    try:
        tournament = Tournament.objects.create(
            name=f"2-Player Tournament {tournament_number}",
            start_date=timezone.now() + timedelta(days=random.randint(1, 365)),
            status=random.choice(['REGISTRATION', 'IN_PROGRESS', 'FINISHED']),
            tournament_type='TWO_PLAYER',
            creator=random.choice(users).id,
            max_participants=2
        )
        print(f"Created 2-Player Tournament: {tournament.name}", file=sys.stderr)

        participants = random.sample(users, 2)
        for user in participants:
            Participation.objects.create(
                user=user,
                tournament=tournament,
                display_name=user.display_name
            )

        # Create a single match for the 2-player tournament
        match = Match2.objects.create(
            tournament=tournament,
            player1=Participation.objects.get(user=participants[0], tournament=tournament),
            player2=Participation.objects.get(user=participants[1], tournament=tournament),
            round=1,
            order=1,
            player1_score=random.randint(0, 21),
            player2_score=random.randint(0, 21)
        )
        match.winner = match.player1 if match.player1_score > match.player2_score else match.player2
        match.save()
        print(f"Created Match2: {match} - Scores: {match.player1_score}-{match.player2_score}", file=sys.stderr)

    except Exception as e:
        print(f"Error creating 2-player tournament: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

def create_four_player_tournament(users, tournament_number):
    try:
        tournament = Tournament.objects.create(
            name=f"4-Player Tournament {tournament_number}",
            start_date=timezone.now() + timedelta(days=random.randint(1, 365)),
            status=random.choice(['REGISTRATION', 'IN_PROGRESS', 'FINISHED']),
            tournament_type='FOUR_PLAYER',
            creator=random.choice(users).id,
            max_participants=4
        )
        print(f"Created 4-Player Tournament: {tournament.name}", file=sys.stderr)

        participants = random.sample(users, 4)
        for user in participants:
            Participation.objects.create(
                user=user,
                tournament=tournament,
                display_name=user.display_name
            )

        # Create two rounds for the 4-player tournament
        for round in range(1, 3):
            match = Match4.objects.create(
                tournament=tournament,
                player1=Participation.objects.get(user=participants[0], tournament=tournament),
                player2=Participation.objects.get(user=participants[1], tournament=tournament),
                player3=Participation.objects.get(user=participants[2], tournament=tournament),
                player4=Participation.objects.get(user=participants[3], tournament=tournament),
                round=round,
                order=1,
                player1_score=random.randint(0, 21),
                player2_score=random.randint(0, 21),
                player3_score=random.randint(0, 21),
                player4_score=random.randint(0, 21)
            )
            scores = [match.player1_score, match.player2_score, match.player3_score, match.player4_score]
            winner_index = scores.index(max(scores))
            match.winner = getattr(match, f'player{winner_index + 1}')
            match.save()
            print(f"Created Match4: {match} - Round: {round} - Scores: {match.player1_score}-{match.player2_score}-{match.player3_score}-{match.player4_score}", file=sys.stderr)

    except Exception as e:
        print(f"Error creating 4-player tournament: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

def create_dummy_data():
    print("Function create_dummy_data started", file=sys.stderr)
    print(f"Total users in auth_user: {User.objects.count()}", file=sys.stderr)
    print(f"Total users in ApiUser: {ApiUser.objects.count()}", file=sys.stderr)

    for user in User.objects.all():
        api_user, created = ApiUser.objects.get_or_create(user=user, defaults={'display_name': user.username})
        if created:
            print(f"Created ApiUser for {user.username}", file=sys.stderr)

    print(f"After creation, total users in ApiUser: {ApiUser.objects.count()}", file=sys.stderr)

    users = list(ApiUser.objects.all())
    if len(users) >= 2:
        for i in range(150):  # Create 150 2-player tournaments
            create_two_player_tournament(users, i+1)
    if len(users) >= 4:
        for i in range(75):  # Create 75 4-player tournaments
            create_four_player_tournament(users, i+1)

    print("Function create_dummy_data finished", file=sys.stderr)

if __name__ == '__main__':
    print("Calling create_dummy_data", file=sys.stderr)
    create_dummy_data()

print("Script finished", file=sys.stderr)