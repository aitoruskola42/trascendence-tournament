from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ..models import Tournament, Participation, Match, ApiUser
from ..serializer import TournamentOpenSerializer, TournamentSerializer, ParticipationSerializer, MatchSerializer
from django.db import models
from django.db.models import Count, F
from django.db.models.functions import Coalesce

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tournament_ready_list(request):
    if request.method == 'GET':
        current_user = request.user.apiuser
        
        # Obtener los IDs de los torneos en los que el usuario está participando
        participating_tournament_ids = Participation.objects.filter(user=current_user).values_list('tournament_id', flat=True)
        print(f"Participating tournament IDs: {list(participating_tournament_ids)}")
        
        # Filtrar los torneos para incluir solo aquellos en los que el usuario está participando
        tournaments = Tournament.objects.filter(
            tournament_type='REGULAR',
            id__in=participating_tournament_ids
        )
        print(f"Tournaments after initial filter: {tournaments.count()}")
        
        # Anotar el número de participantes actuales y filtrar los torneos llenos
        tournaments = tournaments.annotate(
            current_participants=Count('participation')
        )
        print("Tournaments with participant count:")
        for t in tournaments:
            print(f"ID: {t.id}, Max: {t.max_participants}, Current: {t.current_participants}")
        
        # Filtrar para mostrar solo los torneos que están llenos
        tournaments = tournaments.filter(current_participants=F('max_participants'))
        print(f"Final tournaments count: {tournaments.count()}")
        
        serializer = TournamentOpenSerializer(tournaments, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TournamentOpenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user.apiuser)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tournament_open_list(request):
    if request.method == 'GET':
        current_user = request.user.apiuser
        
        # Obtener los IDs de los torneos en los que el usuario ya está participando
        participating_tournament_ids = Participation.objects.filter(user=current_user).values_list('tournament_id', flat=True)
        
        # Filtrar los torneos excluyendo los creados por el usuario y aquellos en los que ya está participando
        tournaments = Tournament.objects.filter(tournament_type='REGULAR').exclude(
            models.Q(creator=current_user.id) | models.Q(id__in=participating_tournament_ids)
        )
        
        # Anotar el número de participantes actuales
        tournaments = tournaments.annotate(
            current_participants=Count('participation')
        )
        
        # Filtrar para mostrar solo los torneos que no están completos
        tournaments = tournaments.filter(current_participants__lt=F('max_participants'))
        
        serializer = TournamentOpenSerializer(tournaments, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TournamentOpenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user.apiuser)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_creator_info(request, creator_id):
    try:
        creator = ApiUser.objects.get(id=creator_id)
        return Response({
            'id': creator.id,
            'username': creator.user.username,
            'display_name': creator.display_name,
          
        })
    except ApiUser.DoesNotExist:
        return Response({'error': 'Creator not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_tournament(request):
    serializer = TournamentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        tournament = serializer.save()

        # Obtener la participación recién creada
        participation = Participation.objects.get(user=request.user.apiuser, tournament=tournament)
        
        # Añadir la información de la participación a la respuesta
        response_data = serializer.data
        response_data['participation'] = {
            'id': participation.id,
            'user_id': participation.user_id,
            'tournament_id': participation.tournament_id,
            'score': participation.score
        }
                
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_tournaments(request):
    try:
        api_user = request.user.apiuser
        tournaments = Tournament.objects.filter(creator=api_user.id)
        serializer = TournamentSerializer(tournaments, many=True)
        return Response({'tournaments': serializer.data})
    except ApiUser.DoesNotExist:
        return Response({'error': 'ApiUser not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tournament_list(request):
    if request.method == 'GET':
        tournaments = Tournament.objects.filter(tournament_type='REGULAR')
        serializer = TournamentSerializer(tournaments, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TournamentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def tournament_detail(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    
    if request.method == 'GET':
        serializer = TournamentSerializer(tournament)
        
        # Imprimir información del torneo
        print("Tournament object:")
        print(f"ID: {tournament.id}")
        print(f"Name: {tournament.name}")
        print(f"Start Date: {tournament.start_date}")
        print(f"Status: {tournament.status}")
        print(f"Tournament Type: {tournament.tournament_type}")
        print(f"Creator: {tournament.creator}")
        print(f"Max Participants: {tournament.max_participants}")
        
        # Imprimir participantes
        participations = Participation.objects.filter(tournament=tournament)
        print("\nParticipants:")
        for participation in participations:
            print(f"- User ID: {participation.user.id}, Name: {participation.user.display_name}, Score: {participation.score}")

        # Imprimir datos serializados
        print("\nSerialized data:")
        print(serializer.data)

        return Response(serializer.data)
   

    elif request.method == 'PUT':
        if request.user != tournament.creator and not request.user.is_staff:
            return Response({'error': 'You do not have permission to edit this tournament'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TournamentSerializer(tournament, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if request.user != tournament.creator and not request.user.is_staff:
            return Response({'error': 'You do not have permission to delete this tournament'}, status=status.HTTP_403_FORBIDDEN)
        tournament.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def join_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    if tournament.status != 'REGISTRATION':
        return Response({'error': 'This tournament is not open for registration'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Obtener el ApiUser correspondiente al usuario autenticado
    api_user = ApiUser.objects.get(user=request.user)
    
    participation, created = Participation.objects.get_or_create(
        tournament=tournament,
        user=api_user,  # Usar api_user en lugar de request.user
        defaults={'display_name': api_user.display_name} 
    )
    
    if not created:
        return Response({'error': 'You are already registered for this tournament'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ParticipationSerializer(participation)
    return Response(serializer.data, status=status.HTTP_201_CREATED)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_tournament(request, pk):
    try:
        api_user = ApiUser.objects.get(user=request.user)
        tournament = Tournament.objects.get(pk=pk, creator=api_user)
        
        if tournament.status != 'REGISTRATION':
            return Response({'error': 'Tournament is not in registration phase'}, status=status.HTTP_400_BAD_REQUEST)
        
        if tournament.participants.count() < 2:
            return Response({'error': 'Not enough participants to start the tournament'}, status=status.HTTP_400_BAD_REQUEST)
        
        tournament.status = 'IN_PROGRESS'
        tournament.save()
        
        # Aquí puedes añadir lógica adicional para iniciar el torneo, como generar los primeros partidos
        
        return Response({'message': 'Tournament started successfully'}, status=status.HTTP_200_OK)
    except ApiUser.DoesNotExist:
        return Response({'error': 'ApiUser not found'}, status=status.HTTP_404_NOT_FOUND)
    except Tournament.DoesNotExist:
        return Response({'error': 'Tournament not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_one_vs_one_match(request):
    player1 = request.user
    player2_id = request.data.get('player2_id')
    
    if not player2_id:
        return Response({'error': 'Player 2 is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        player2 = User.objects.get(id=player2_id)
    except User.DoesNotExist:
        return Response({'error': 'Player 2 not found'}, status=status.HTTP_404_NOT_FOUND)
    
    one_vs_one_tournament = Tournament.get_or_create_one_vs_one_tournament()
    
    participation1, _ = Participation.objects.get_or_create(
        tournament=one_vs_one_tournament,
        user=player1,
        defaults={'alias': player1.username}
    )
    
    participation2, _ = Participation.objects.get_or_create(
        tournament=one_vs_one_tournament,
        user=player2,
        defaults={'alias': player2.username}
    )
    
    match = Match.create_one_vs_one_match(participation1, participation2)
    
    serializer = MatchSerializer(match)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_one_vs_one_matches(request):
    one_vs_one_tournament = Tournament.get_or_create_one_vs_one_tournament()
    matches = Match.objects.filter(tournament=one_vs_one_tournament)
    serializer = MatchSerializer(matches, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def end_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    if tournament.status != 'IN_PROGRESS':
        return Response({'error': 'This tournament is not in progress'}, status=status.HTTP_400_BAD_REQUEST)
    
    tournament.status = 'FINISHED'
    tournament.save()
    # Here you would add logic to determine the winner and update rankings
    return Response({'status': 'Tournament ended successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_tournaments(request):
    tournaments = Tournament.objects.filter(creator=request.user.apiuser).prefetch_related('participants')
    serializer = TournamentSerializer(tournaments, many=True)
    return Response(serializer.data)