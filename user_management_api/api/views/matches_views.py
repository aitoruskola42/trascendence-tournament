from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Match, Game, GameEvent
#from ..serializers import MatchSerializer, GameSerializer, GameEventSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match_list(request):
    matches = Match.objects.all()
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    serializer = MatchSerializer(match)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if match.games.exists():
        return Response({'error': 'This match has already started'}, status=status.HTTP_400_BAD_REQUEST)
    
    game = Game.objects.create(match=match)
    serializer = GameSerializer(game)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_point(request, match_pk, game_pk):
    match = get_object_or_404(Match, pk=match_pk)
    game = get_object_or_404(Game, pk=game_pk, match=match)
    
    scoring_player = request.data.get('scoring_player')
    if scoring_player not in ['player1', 'player2']:
        return Response({'error': 'Invalid scoring player'}, status=status.HTTP_400_BAD_REQUEST)
    
    if scoring_player == 'player1':
        game.player1_score += 1
        scoring_participation = match.player1
    else:
        game.player2_score += 1
        scoring_participation = match.player2
    
    game.save()
    
    event = GameEvent.objects.create(
        game=game,
        event_type='POINT',
        player=scoring_participation,
        details={'new_score': {
            'player1': game.player1_score,
            'player2': game.player2_score
        }}
    )
    
    # Check if the game is over
    if game.player1_score >= 11 and game.player1_score - game.player2_score >= 2:
        game.winner = match.player1
        game.end_time = event.timestamp
        game.save()
    elif game.player2_score >= 11 and game.player2_score - game.player1_score >= 2:
        game.winner = match.player2
        game.end_time = event.timestamp
        game.save()
    
    # Check if the match is over
    if game.winner:
        games_won = Game.objects.filter(match=match, winner=game.winner).count()
        if games_won >= 2:  # Assuming best of 3
            match.winner = game.winner
            match.player1_score = Game.objects.filter(match=match, winner=match.player1).count()
            match.player2_score = Game.objects.filter(match=match, winner=match.player2).count()
            match.save()
    
    serializer = GameEventSerializer(event)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pause_game(request, match_pk, game_pk):
    match = get_object_or_404(Match, pk=match_pk)
    game = get_object_or_404(Game, pk=game_pk, match=match)
    
    event = GameEvent.objects.create(
        game=game,
        event_type='PAUSE'
    )
    
    serializer = GameEventSerializer(event)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resume_game(request, match_pk, game_pk):
    match = get_object_or_404(Match, pk=match_pk)
    game = get_object_or_404(Game, pk=game_pk, match=match)
    
    event = GameEvent.objects.create(
        game=game,
        event_type='RESUME'
    )
    
    serializer = GameEventSerializer(event)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def game_events(request, match_pk, game_pk):
    match = get_object_or_404(Match, pk=match_pk)
    game = get_object_or_404(Game, pk=game_pk, match=match)
    
    events = GameEvent.objects.filter(game=game).order_by('timestamp')
    serializer = GameEventSerializer(events, many=True)
    return Response(serializer.data)