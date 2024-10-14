# Django imports
from django.http import JsonResponse  # Provides a JSON-formatted HTTP response
from django.shortcuts import redirect  # Function for redirecting to a specific URL
from django.conf import settings  # Access to Django project settings
from django.contrib.auth import login, logout, authenticate, get_user_model  # Authentication functions
from django.contrib.auth.models import User as DjangoUser  # Django's built-in User model
from django.utils import timezone  # Utilities for working with dates and times
from django.core.serializers.json import DjangoJSONEncoder  # JSON encoder for Django objects

# Django Rest Framework imports
from rest_framework.decorators import api_view  # Decorator for API views
from rest_framework.response import Response  # REST framework's Response class
from rest_framework import status  # Provides HTTP status codes
from rest_framework.authtoken.models import Token  # Token model for authentication
from rest_framework.request import Request

# OAuth2 related imports
from requests_oauthlib import OAuth2Session  # Provides OAuth 2.0 support
from oauth2_provider.models import AccessToken  # Model for OAuth2 access tokens

# Simple JWT imports
from rest_framework_simplejwt.tokens import RefreshToken  # Handles refresh tokens for JWT

# Third-party library imports
import pyotp  # Implements TOTP (Time-based One-Time Password) algorithm for 2FA
import time

# Python standard library imports
import json  # Provides JSON encoding and decoding functionality
import logging  # Logging facility for Python
from datetime import timedelta  # For working with durations

# Local imports
from .models import ApiUser  # Custom ApiUser model

User = get_user_model()  # Get the active User model
logger = logging.getLogger(__name__)  # Creates a logger instance for this module


@api_view(['POST'])
def oauth_verify_2fa(request):
    user_id = request.data.get('user_id')
    code = request.data.get('code')
    
    logger.debug(f"Received 2FA verification request for user_id: {user_id}, code: {code}")

    if not user_id or not code:
        return Response({'error': 'User ID and code are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
        logger.debug(f"User found: {user.username}")
    except User.DoesNotExist:
        logger.error(f"User not found for OAuth 2FA verification: {user_id}")
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    totp = pyotp.TOTP(user.apiuser.two_factor_secret)
    current_time = int(time.time())

    logger.debug(f"TOTP secret for user {user.username}: {user.apiuser.two_factor_secret}")
    logger.debug(f"Current TOTP code: {totp.now()}")
    logger.debug(f"Received code: {code}")
    logger.debug(f"Current timestamp: {current_time}")
    logger.debug(f"TOTP at t-30s: {totp.at(for_time=current_time - 30)}")
    logger.debug(f"TOTP at t+30s: {totp.at(for_time=current_time + 30)}")

    if totp.verify(code, valid_window=2):  # Esto permite una ventana de ±60 segundos
        logger.info(f"OAuth 2FA verification successful for user {user.username}")
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user.apiuser.get_full_user_data()
        })
    else:
        logger.warning(f"OAuth 2FA verification failed for user {user.username}. Received code: {code}, Expected code: {totp.now()}")
        return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)

def get_oauth_session(state=None):
    return OAuth2Session(
        settings.OAUTH2_CLIENT_ID,
        redirect_uri=settings.OAUTH2_REDIRECT_URI,
        state=state
    )

def auth_login(request):
    oauth = get_oauth_session()
    authorization_url, state = oauth.authorization_url(settings.OAUTH2_AUTH_URL)
    request.session['oauth_state'] = state
    logger.debug(f"Authorization URL: {authorization_url}")
    return redirect(authorization_url)


def auth_callback(request):
    oauth = get_oauth_session(state=request.session.get('oauth_state'))
    try:
        token = oauth.fetch_token(
            settings.OAUTH2_TOKEN_URL,
            client_secret=settings.OAUTH2_CLIENT_SECRET,
            authorization_response=request.build_absolute_uri()
        )
        logger.debug(f"Token obtenido: {token}")
        request.session['oauth_token'] = token
        user_info = get_user_info(request)
        logger.debug(f"Información del usuario: {user_info}")
        
        if user_info:
            user = create_or_update_user(user_info)
            
            if user.apiuser.two_factor_enabled:
                request.session['oauth_user_id'] = user.id
                logger.info(f"OAuth login requires 2FA for user: {user.username}")
                return redirect(f"{settings.LOGIN_REDIRECT_URL}?oauth2fa={user.id}")
            
            # Si no se requiere 2FA, continúa con el proceso normal
            refresh = RefreshToken.for_user(user)
            response_data = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': json.dumps(user.apiuser.get_full_user_data())
            }
            
            redirect_url = f"{settings.LOGIN_REDIRECT_URL}#" + "&".join([f"{key}={value}" for key, value in response_data.items()])
            return redirect(redirect_url)
        else:
            logger.error("No se pudo obtener la información del usuario")
            return JsonResponse({'error': 'No se pudo obtener la información del usuario'}, status=400)
    except Exception as e:
        logger.exception(f"Error en auth_callback: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)

def get_user_info(request):
    token = request.session.get('oauth_token')
    if not token:
        logger.error("No token found in session")
        return None
    oauth = OAuth2Session(settings.OAUTH2_CLIENT_ID, token=token)
    try:
        user_info = oauth.get(settings.OAUTH2_API_BASE_URL + 'me').json()
        return user_info
    except Exception as e:
        logger.exception(f"Error fetching user info: {str(e)}")
        return None


def create_or_update_user(user_info):
    oauth_id = str(user_info['id'])
    email = user_info.get('email', '')
    username = user_info['login']
    
    logger.debug(f"Procesando usuario OAuth: {username}")

    try:
        api_user = ApiUser.objects.get(oauth_id=oauth_id)
        user = api_user.user
        logger.info(f"Usuario existente encontrado: {user.username}")
        created = False
    except ApiUser.DoesNotExist:
        user, created = User.objects.get_or_create(username=username)
        if created:
            logger.info(f"Nuevo usuario creado: {username}")
            user.email = email
            user.set_unusable_password()
            user.is_active = True
            user.save()
        
        api_user = ApiUser.objects.create(
            user=user,
            oauth_id=oauth_id,
            user_42=True
        )
        logger.info(f"Nuevo ApiUser creado para: {username}")

    user.email = email
    user.first_name = user_info.get('first_name', '')
    user.last_name = user_info.get('last_name', '')
    user.save()

    api_user.user_42 = True
    
    # Removemos la configuración automática de 2FA
    if created:
        logger.info(f"Nuevo usuario OAuth creado: {username}. 2FA no configurado automáticamente.")
    else:
        logger.info(f"Información de 2FA para usuario existente: {username}. Enabled: {api_user.two_factor_enabled}, Secret: {api_user.two_factor_secret}")

    api_user.save()
    
    logger.info(f"Usuario actualizado/creado exitosamente: {username}")
    return user


def auth_logout(request):
    logout(request)
    return JsonResponse({"message": "Has cerrado sesión exitosamente."})