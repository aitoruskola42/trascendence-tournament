from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models  # Añade esta línea
from .models import Match
from .serializer import MatchSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse  # Provides a JSON-formatted HTTP response
import json  # Provides JSON encoding and decoding functionality
import logging
from django.db import connection
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import pytz

def stats_view(request, user_id):
    # Partidas individuales
    individual_matches = Match.objects.filter(
        Q(player1_id=user_id) | Q(player2_id=user_id),
        match_type='INDIVIDUAL',
        tournament_id=0
    )
    individual_played = individual_matches.count()
    individual_won = individual_matches.filter(winner_id=user_id).count()

    # Partidas de torneo
    tournament_matches = Match.objects.filter(
        Q(player1_id=user_id) | Q(player2_id=user_id),
        tournament_id__gt=0
    )
    tournaments_played = tournament_matches.filter(match_type='SEMIFINAL').count()
    tournaments_won = tournament_matches.filter(match_type='FINAL', winner_id=user_id).count()

    # Total de partidas
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

@csrf_exempt
def semifinal_winners(request, tournament_id):
    if request.method == 'GET':
        try:
            semifinal_matches = Match.objects.filter(tournament_id=tournament_id, match_type='SEMIFINAL')
            winners = [match.winner_id for match in semifinal_matches if match.winner_id]
            
            return JsonResponse({
                "status": "success",
                "tournament_id": tournament_id,
                "winners": winners
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)

@csrf_exempt
def end_tournament(request, tournament_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            winner_id = data.get('winner_id')
            
            if not winner_id:
                return JsonResponse({"status": "error", "message": "winner_id es requerido"}, status=400)
            
            tournament = Tournament.objects.get(id=tournament_id)
            tournament.winner_id = winner_id
            tournament.save()
            
            return JsonResponse({
                "status": "success",
                "message": "Torneo finalizado exitosamente",
                "tournament_id": tournament_id,
                "winner_id": winner_id
            })
        except Tournament.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Torneo no encontrado"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Datos JSON inválidos"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)

@api_view(['GET'])
def match_list(request):
    matches = Match.objects.all()
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def match4_list(request):
    matches = Match.objects.all()
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def match_list_id(request, pk):
    matches = Match.objects.filter(
        (Q(player1_id=pk) | Q(player2_id=pk)) &
        (Q(match_type='INDIVIDUAL') )
    )
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def match4_list_id(request, pk):
    matches = Match.objects.filter(
        (Q(player1_id=pk) | Q(player2_id=pk)) &
        (Q(match_type='SEMIFINAL') | Q(match_type='FINAL'))
    )
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)

@csrf_exempt
def register_tournament(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_date = data.get('start_date')
            
            if not start_date:
                return JsonResponse({"status": "error", "message": "La fecha de inicio es requerida"}, status=400)
            
            tournament = Tournament.objects.create(
                start_date=timezone.datetime.fromisoformat(start_date),
                winner_id=data.get('winner_id', 0)  # Por defecto 0 si no se proporciona
            )
            
            return JsonResponse({
                "status": "success",
                "message": "Torneo registrado exitosamente",
                "tournament_id": tournament.id
            })
        
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Datos JSON inválidos"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)

@csrf_exempt
def game_result(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Match.objects.create(
            tournament_id=data.get('tournament_id'),
            player1_id=data.get('player1_id'),
            player2_id=data.get('player2_id'),
            player1_display_name=data.get('player1_display_name'),
            player2_display_name=data.get('player2_display_name'),
            player1_score=data.get('player1_score'),
            player2_score=data.get('player2_score'),
            match_type=data.get('match_type'),
            winner_id=data.get('winner_id'),
            date=datetime.now(pytz.UTC)
        )
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)
