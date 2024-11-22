from django.http import JsonResponse
from django.db.models import Q
from rest_framework.response import Response

from .models import Match
from .serializer import MatchSerializer

def stats_view(request, user_id):
    individual_matches = Match.objects.filter(
        Q(player1_id=user_id) | Q(player2_id=user_id),
        match_type='INDIVIDUAL',
        tournament_id=0
    )
    individual_played = individual_matches.count()
    individual_won = individual_matches.filter(winner_id=user_id).count()
    tournament_matches = Match.objects.filter(
        Q(player1_id=user_id) | Q(player2_id=user_id),
        tournament_id__gt=0
    )
    tournaments_played = tournament_matches.filter(match_type='SEMIFINAL').count()
    tournaments_won = tournament_matches.filter(match_type='FINAL', winner_id=user_id).count()
    total_played = individual_played + tournaments_played
    total_won = individual_won + tournaments_won

    stats = {
        "individual_matches": {
            "played": individual_played,
            "won": individual_won
        },
        "tournaments": {
            "played": tournaments_played,
            "won": tournaments_won
        },
        "total": {
            "played": total_played,
            "won": total_won
        }
    }

    return JsonResponse(stats)

def match_list_id(request, pk):
    matches = Match.objects.filter(
        (Q(player1_id=pk) | Q(player2_id=pk)) &
        (Q(match_type='INDIVIDUAL') )
    )
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)

def match4_list_id(request, pk):
    matches = Match.objects.filter(
        (Q(player1_id=pk) | Q(player2_id=pk)) &
        (Q(match_type='SEMIFINAL') | Q(match_type='FINAL'))
    )
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)
