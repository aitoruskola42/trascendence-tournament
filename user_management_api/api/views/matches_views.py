from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models  # Añade esta línea
from ..models import Match2, Match4, Tournament, Participation
from ..serializer import Match4Serializer, MatchDetail4Serializer,  Match2Serializer, MatchDetail2Serializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match4_list(request):
    matches = Match4.objects.filter(
        models.Q(player1__user=request.user.apiuser) | 
        models.Q(player2__user=request.user.apiuser) |
        models.Q(player3__user=request.user.apiuser) |
        models.Q(player4__user=request.user.apiuser)
    ).select_related(
        'player1__user', 'player2__user', 'player3__user', 'player4__user',
        'winner__user', 'tournament'
    )
    serializer = Match4Serializer(matches, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match4_detail(request, pk):
    match = get_object_or_404(Match4, pk=pk)
    serializer = MatchDetail4Serializer(match)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start4_match(request, pk):
    match = get_object_or_404(Match4, pk=pk)
    
    if not hasattr(match, 'status'):
        return Response({'error': 'Match status not defined'}, status=status.HTTP_400_BAD_REQUEST)
    
    if match.status != 'PENDING':
        return Response({'error': 'This match has already started or finished'}, status=status.HTTP_400_BAD_REQUEST)
    
    match.status = 'IN_PROGRESS'
    match.save()
    
    serializer = Match4Serializer(match)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_match4_score(request, pk):
    match = get_object_or_404(Match4, pk=pk)
    
    if not hasattr(match, 'status'):
        return Response({'error': 'Match status not defined'}, status=status.HTTP_400_BAD_REQUEST)
    
    if match.status != 'IN_PROGRESS':
        return Response({'error': 'This match is not in progress'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar puntuaciones
    players = [match.player1, match.player2, match.player3, match.player4]
    for i, player in enumerate(players, start=1):
        score = request.data.get(f'player{i}_score')
        if score is not None:
            setattr(match, f'player{i}_score', int(score))
    
    match.save()
    
    # Comprobar si el partido ha terminado
    if hasattr(match, 'is_finished') and callable(getattr(match, 'is_finished')):
        if match.is_finished():
            match.status = 'FINISHED'
            if hasattr(match, 'determine_winner') and callable(getattr(match, 'determine_winner')):
                match.determine_winner()
            match.save()
    
    serializer = Match4Serializer(match)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match2_list(request):
    matches = Match2.objects.filter(
        models.Q(player1__user=request.user.apiuser) | 
        models.Q(player2__user=request.user.apiuser) 
    ).select_related(
        'player1__user', 'player2__user',
        'winner__user', 'tournament'
    )
    serializer = Match2Serializer(matches, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match2_detail(request, pk):
    match = get_object_or_404(Match4, pk=pk)
    serializer = MatchDetail2Serializer(match)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start2_match(request, pk):
    match = get_object_or_404(Match2, pk=pk)
    
    if not hasattr(match, 'status'):
        return Response({'error': 'Match status not defined'}, status=status.HTTP_400_BAD_REQUEST)
    
    if match.status != 'PENDING':
        return Response({'error': 'This match has already started or finished'}, status=status.HTTP_400_BAD_REQUEST)
    
    match.status = 'IN_PROGRESS'
    match.save()
    
    serializer = Match2Serializer(match)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_match2_score(request, pk):
    match = get_object_or_404(Match2, pk=pk)
    
    if not hasattr(match, 'status'):
        return Response({'error': 'Match status not defined'}, status=status.HTTP_400_BAD_REQUEST)
    
    if match.status != 'IN_PROGRESS':
        return Response({'error': 'This match is not in progress'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar puntuaciones
    players = [match.player1, match.player2, match.player3, match.player4]
    for i, player in enumerate(players, start=1):
        score = request.data.get(f'player{i}_score')
        if score is not None:
            setattr(match, f'player{i}_score', int(score))
    
    match.save()
    
    # Comprobar si el partido ha terminado
    if hasattr(match, 'is_finished') and callable(getattr(match, 'is_finished')):
        if match.is_finished():
            match.status = 'FINISHED'
            if hasattr(match, 'determine_winner') and callable(getattr(match, 'determine_winner')):
                match.determine_winner()
            match.save()
    
    serializer = Match2Serializer(match)
    return Response(serializer.data)