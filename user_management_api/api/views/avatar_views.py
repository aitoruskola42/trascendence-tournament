# Django imports
from django.contrib.auth import authenticate  # Handles user authentication
from django.contrib.auth.models import User as DjangoUser  # Django's built-in User model
from django.conf import settings  # Access to Django project settings
from django.http import HttpResponse, FileResponse  # HTTP response classes

# Rest Framework imports
from rest_framework import status  # HTTP status codes
from rest_framework.decorators import api_view, authentication_classes, permission_classes  # Decorators for API views
from rest_framework.response import Response  # REST framework's Response class
from rest_framework.authentication import TokenAuthentication  # Token-based authentication
from rest_framework.authtoken.models import Token  # Token model for authentication
from rest_framework.permissions import IsAuthenticated  # Permission class to ensure user is authenticated

# Simple JWT imports
from rest_framework_simplejwt.tokens import RefreshToken  # Handles refresh tokens for JWT
from rest_framework_simplejwt.authentication import JWTAuthentication  # JWT authentication backend

# Local imports
from ..models import ApiUser  # Custom User and ApiUser models
from ..serializer import UserSerializer, ApiUserSerializer  # Serializers for User and ApiUser models

# Python standard library imports
import os  # Operating system interface, for file and path operations
import logging  # Logging facility for Python

logger = logging.getLogger(__name__)

def get_default_avatar(request):
    default_path = os.path.join(settings.MEDIA_ROOT, 'default.jpg')
    logger.info(f"Attempting to serve default avatar from: {default_path}")
    if os.path.exists(default_path):
        return FileResponse(open(default_path, 'rb'), content_type="image/jpeg")
    else:
        logger.error(f"Default avatar not found at: {default_path}")
        return HttpResponse("Default avatar not found", status=404)

@api_view(['GET'])
def get_avatar(request, user_id):
    logger.info(f"Attempting to get avatar for user {user_id}")
    try:
        api_user = ApiUser.objects.get(user__id=user_id)
        if api_user.avatar_image:
            file_path = api_user.avatar_image.path
            logger.info(f"Avatar path for user {user_id}: {file_path}")
            if os.path.exists(file_path):
                return FileResponse(open(file_path, 'rb'), content_type="image/jpeg")
            else:
                logger.warning(f"Avatar file not found: {file_path}")
        else:
            logger.warning(f"No avatar_image for user: {user_id}")
    except ApiUser.DoesNotExist:
        logger.warning(f"ApiUser not found for user_id: {user_id}")
    except Exception as e:
        logger.error(f"Error retrieving avatar: {str(e)}")
    
    # Si no se encuentra la imagen o el usuario, devolver una imagen por defecto
    return get_default_avatar(request)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    if 'avatar_image' not in request.FILES:
        return Response({'error': 'No file was submitted'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['avatar_image']
    user = request.user
    try:
        api_user = ApiUser.objects.get(user=user)
        
        # Guardar la imagen
        file_name = f'avatar_{user.id}.{file.name.split(".")[-1]}'
        api_user.avatar_image.save(file_name, file, save=True)
        
        logger.info(f"Avatar saved for user {user.id} at: {api_user.avatar_image.path}")
        
        return Response({
            'message': 'Avatar uploaded successfully',
            'path': api_user.avatar_image.url
        }, status=status.HTTP_200_OK)
    except ApiUser.DoesNotExist:
        logger.error(f"ApiUser not found for user: {user.id}")
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error uploading avatar for user {user.id}: {str(e)}")
        return Response({'error': f'An error occurred while uploading the avatar: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)