from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models  # Añade esta línea
from ..models import Match, Tournament
from ..serializer import MatchSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse  # Provides a JSON-formatted HTTP response
import json  # Provides JSON encoding and decoding functionality
import logging
from django.db import connection
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.db.models import Q


from datetime import datetime, timedelta
import pytz




@api_view(['GET'])
def match_list(request):
    logger.debug(f"User: {request.user}")
    logger.debug(f"Auth: {request.auth}")
    matches = Match.objects.all()
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def match4_list(request):
    logger.debug(f"User: {request.user}")
    logger.debug(f"Auth: {request.auth}")
    matches = Match.objects.all()
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def match_list_id(request, pk):
    logger.debug(f"User: {request.user}")
    logger.debug(f"Auth: {request.auth}")

    matches = Match.objects.filter(
        (Q(player1_id=pk) | Q(player2_id=pk)) &
        (Q(match_type='INDIVIDUAL') )
    )
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def match4_list_id(request, pk):
    logger.debug(f"User: {request.user}")
    logger.debug(f"Auth: {request.auth}")

    matches = Match.objects.filter(
        (Q(player1_id=pk) | Q(player2_id=pk)) &
        (Q(match_type='SEMIFINAL') | Q(match_type='FINAL'))
    )

    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)



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

logger = logging.getLogger(__name__)  # Creates a logger instance for this module

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
