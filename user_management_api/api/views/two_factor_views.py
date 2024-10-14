# Django Rest Framework imports
from rest_framework.decorators import api_view, permission_classes  # Decorators for API views
from rest_framework.response import Response  # REST framework's Response class
from rest_framework import status  # Provides HTTP status codes
from rest_framework.permissions import IsAuthenticated  # Permission class to ensure user is authenticated

# Third-party library imports
import pyotp  # Implements TOTP (Time-based One-Time Password) algorithm for 2FA
import qrcode  # Generates QR codes
import base64  # Provides functions for encoding binary data to ASCII characters and decoding it

# Python standard library imports
from io import BytesIO  # Implements a file-like object that reads and writes a bytes string
import logging  # Provides a flexible framework for generating log messages

# Local imports
from ..models import ApiUser  # Custom ApiUser model
logger = logging.getLogger(__name__)  # Creates a logger instance for this module
import time



@api_view(['POST'])
def oauth_verify_2fa(request):
    user_id = request.session.get('oauth_user_id')
    if not user_id:
        logger.error("OAuth 2FA verification attempted without user_id in session")
        return Response({'error': 'Invalid session'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(id=user_id)
    code = request.data.get('code')

    if not code:
        logger.warning(f"OAuth 2FA verification attempted without code for user {user.username}")
        return Response({'error': 'Verification code is required'}, status=status.HTTP_400_BAD_REQUEST)

    totp = pyotp.TOTP(user.apiuser.two_factor_secret)
    if totp.verify(code):
        logger.info(f"OAuth 2FA verification successful for user {user.username}")
        refresh = RefreshToken.for_user(user)
        # Limpiar la sesión
        del request.session['oauth_user_id']
        response_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': json.dumps(user.apiuser.get_full_user_data())
        }
        return Response(response_data)
    else:
        logger.warning(f"OAuth 2FA verification failed for user {user.username}")
        return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    user = request.user.apiuser
    if user.two_factor_enabled:
        logger.info(f"User {user.user.username} attempted to enable 2FA when it's already enabled")
        return Response({'error': '2FA is already enabled'}, status=status.HTTP_400_BAD_REQUEST)
    
    secret = pyotp.random_base32()
    user.two_factor_secret = secret
    user.two_factor_enabled = True
    user.save()

    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(user.user.username, issuer_name="42 ft_transcendence")

    img = qrcode.make(uri)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code = base64.b64encode(buffered.getvalue()).decode()

    logger.info(f"2FA enabled for user {user.user.username}")
    return Response({
        'secret': secret,
        'qr_code': qr_code
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    logger.debug(f"Received 2FA verification request: {request.data}")
    
    code = request.data.get('code')
    if not code:
        logger.warning("No verification code provided")
        return Response({'error': 'Verification code is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = request.user.apiuser
    except AttributeError:
        logger.error(f"ApiUser not found for user {request.user.username}")
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

    totp = pyotp.TOTP(user.two_factor_secret)
    current_time = int(time.time())

    logger.debug(f"Secret: {user.two_factor_secret}")
    logger.debug(f"Current time: {current_time}")
    logger.debug(f"Generated code: {totp.now()}")
    logger.debug(f"Received code: {code}")

    # Aumentar la ventana de tiempo
    if totp.verify(code, valid_window=15):  # Aumentado a 15 (7.5 minutos antes y después)
        logger.info(f"2FA verification successful for user {user.user.username}")
        user.two_factor_configured = True
        user.save()
        return Response({'message': '2FA verification successful'})
    else:
        logger.warning(f"Invalid 2FA code for user {user.user.username}")
        return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    user = request.user.apiuser
    if not user.two_factor_enabled:
        return Response({'error': '2FA is not enabled'}, status=status.HTTP_400_BAD_REQUEST)

    user.two_factor_enabled = False
    user.two_factor_secret = None
    user.save()

    return Response({'message': '2FA has been disabled'})