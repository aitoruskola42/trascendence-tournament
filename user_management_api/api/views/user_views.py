# Django imports
from django.contrib.auth import authenticate  # Handles user authentication
from django.contrib.auth.models import User as DjangoUser  # Django's built-in User model
from django.contrib.auth.decorators import login_required  # Decorator to restrict access to logged-in users
from django.conf import settings  # Access to Django project settings
from django.http import HttpResponse, JsonResponse  # HTTP response classes

# Django Rest Framework imports
from rest_framework import status  # Provides HTTP status codes
from rest_framework.decorators import api_view, authentication_classes, permission_classes  # Decorators for API views
from rest_framework.response import Response  # REST framework's Response class
from rest_framework.authentication import TokenAuthentication  # Token-based authentication
from rest_framework.authtoken.models import Token  # Token model for authentication
from rest_framework.permissions import IsAuthenticated  # Permission class to ensure user is authenticated

# Simple JWT imports
from rest_framework_simplejwt.tokens import RefreshToken  # Handles refresh tokens for JWT
from rest_framework_simplejwt.authentication import JWTAuthentication  # JWT authentication backend

# Third-party library imports
import pyotp  # Implements TOTP (Time-based One-Time Password) algorithm for 2FA

# Python standard library imports
import os  # Operating system interface, for file and path operations
import logging  # Logging facility for Python

# Local imports
from ..models import ApiUser  # Custom User and ApiUser models
from ..serializer import UserSerializer, ApiUserSerializer, TournamentSerializer  # Serializers for User and ApiUser models

logger = logging.getLogger(__name__)  # Creates a logger instance for this module
logging.basicConfig(filename='myapp.log', level=logging.DEBUG)  # Configures basic logging to a file


def get_participations_by_user_id(user_id):
    try:
        # Obtén la instancia de ApiUser usando el ID del usuario
        api_user = ApiUser.objects.get(user__id=user_id)  # Aquí se usa el ID del modelo User
        participations = Participation.objects.filter(user=api_user)  # Filtra participaciones usando la instancia de ApiUser
        return participations
    except ApiUser.DoesNotExist:
        return None  # Maneja el caso donde el ApiUser no existe


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_participations(request, user_id):
    participations = get_participations_by_user_id(user_id)
    if participations is not None:
        # Serializa y devuelve las participaciones
        serializer = ParticipationSerializer(participations, many=True)
        return Response(serializer.data)
    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_list(request):

    users = ApiUser.objects.all().values('user__id', 'user__username')
    return Response(list(users))



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
    except TokenError:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    user = request.user
    return Response({
        'user_id': user.id,
        'username': user.username,
    })


def logout(request):
    # Revoca el token de 42
    token = request.auth.key
    response = requests.post('https://api.intra.42.fr/oauth/token/info', headers={
        'Authorization': f'Bearer {token}'
    })
    
    if response.status_code == 200:
        # El token es válido, procede a revocarlo
        revoke_response = requests.post('https://api.intra.42.fr/oauth/token/revoke', data={
            'client_id': settings.FORTYTWO_CLIENT_ID,
            'client_secret': settings.FORTYTWO_CLIENT_SECRET,
            'token': token
        })
        
        if revoke_response.status_code == 200:
            # Token revocado exitosamente
            # Aquí puedes eliminar el token de tu base de datos si lo almacenas
            request.auth.delete()
            return Response({"message": "Logged out successfully"})
        else:
            return Response({"error": "Failed to revoke token"}, status=400)
    else:
        # El token ya no es válido, simplemente elimínalo de tu sistema
        request.auth.delete()
        return Response({"message": "Logged out successfully"})

@login_required
def check_auth(request):
    return JsonResponse({
        'authenticated': True,
        'username': request.user.username,
        'token': request.session.get('oauth_token')
    })


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": "Tienes acceso a esta vista protegida"})

def home(request):
    if request.user.is_authenticated:
        return HttpResponse(f"Bienvenido, {request.user.username}! <a href='/oauth/logout/'>Cerrar sesión</a> | <a href='/protected/'>Vista protegida</a>")
    else:
        return HttpResponse("Bienvenido, visitante! <a href='/oauth/login/'>Iniciar sesión con 42</a>")

def get_auth_url(request):
    auth_url = f"{settings.OAUTH2_AUTH_URL}?client_id={settings.OAUTH2_CLIENT_ID}&redirect_uri={settings.OAUTH2_REDIRECT_URI}&response_type=code"
    return JsonResponse({"auth_url": auth_url})

def oauth_login(request):
    auth_url = f"{settings.OAUTH2_AUTH_URL}?client_id={settings.OAUTH2_CLIENT_ID}&redirect_uri={settings.OAUTH2_REDIRECT_URI}&response_type=code"
    return redirect(auth_url)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user

    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        return Response({"error": "Both current and new password are required"}, 
                        status=status.HTTP_400_BAD_REQUEST)

    # Verificar la contraseña actual
    if not authenticate(username=user.username, password=current_password):
        return Response({"error": "Current password is incorrect"}, 
                        status=status.HTTP_400_BAD_REQUEST)

    # Cambiar la contraseña
    user.set_password(new_password)
    user.save()

    return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    try:
        django_user = request.user 
        api_user = ApiUser.objects.get(user=django_user)
    except (DjangoUser.DoesNotExist, ApiUser.DoesNotExist):
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    logger.error(f"Received login request for display_name: {request.data.get('display_name')}")
    # Actualizar los campos del usuario Django
    django_user.first_name = request.data.get('first_name', django_user.first_name)
    django_user.last_name = request.data.get('last_name', django_user.last_name)
    django_user.save()


    # Actualizar los campos del ApiUser
    api_user.friends = request.data.get('friends', api_user.friends)
    new_display_name = request.data.get('display_name')
    if new_display_name:
        # Verificar si el nuevo display_name ya está en uso
        if ApiUser.objects.filter(display_name=new_display_name).exclude(user=django_user).exists():
            return Response({"error": "Este nombre de visualización ya está en uso."}, status=status.HTTP_400_BAD_REQUEST)
        api_user.display_name = new_display_name
    api_user.save()

    # Devolver los datos actualizados
    updated_data = api_user.get_full_user_data()
    return Response(updated_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        api_user = ApiUser.objects.get(user=request.user)
        return Response(api_user.get_full_user_data())
    except ApiUser.DoesNotExist:
        return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def login_user(request):
    logger.debug(f"Received login request for user: {request.data.get('username')}")
    username = request.data.get('username')
    password = request.data.get('password')
    two_factor_code = request.data.get('two_factor_code')

    user = authenticate(username=username, password=password)
    
    if user:
        try:
            api_user = ApiUser.objects.get(user=user)
            if api_user.two_factor_enabled:
                if not two_factor_code:
                    logger.info(f"2FA required for user {username}")
                    return Response({'require_2fa': True}, status=status.HTTP_200_OK)
                
                totp = pyotp.TOTP(api_user.two_factor_secret)
                if not totp.verify(two_factor_code):
                    logger.warning(f"Invalid 2FA code for user {username}")
                    return Response({'error': 'Invalid 2FA code'}, status=status.HTTP_400_BAD_REQUEST)

        except ApiUser.DoesNotExist:
            logger.error(f"ApiUser not found for user: {username}")
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        logger.info(f"User {username} logged in successfully")
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username
        })
    
    logger.warning(f"Invalid login attempt for user: {username}")
    return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def sign_out_user(request):
    try:
        # Obtener el token del usuario actual
        token = request.auth

        if token:
            # Eliminar el token
            token.delete()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No active session found."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def get_user(request, pk):
    try:
        api_user = ApiUser.objects.get(user__id=pk)
        return Response(api_user.get_full_user_data())
    except ApiUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_users(request):
    api_users = ApiUser.objects.all()
    user_data = [api_user.get_full_user_data() for api_user in api_users]
    return Response(user_data)


""" @api_view(['GET'])
def get_user(request, pk):
    try:
        user = ApiUser.objects.get(pk=pk)
        full_data = user.get_full_user_data()
        return Response(full_data)
    except ApiUser.DoesNotExist:
        return  Response(status=status.HTTP_404_NOT_FOUND)
"""


@api_view(['POST'])
def create_user(request):
    serializer = ApiUserSerializer(data=request.data)
    if serializer.is_valid():
        api_user = serializer.save()
        return Response(api_user.get_full_user_data(), status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_tournaments(request, user_id):
    try:
        user = ApiUser.objects.get(id=user_id)
        tournaments = user.participated_tournaments.all()
        serializer = TournamentSerializer(tournaments, many=True)
        return Response(serializer.data)
    except ApiUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

