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
from ..models import User, ApiUser  # Custom User and ApiUser models
from ..serializer import UserSerializer, ApiUserSerializer  # Serializers for User and ApiUser models


logger = logging.getLogger(__name__)  # Creates a logger instance for this module
logging.basicConfig(filename='myapp.log', level=logging.DEBUG)  # Configures basic logging to a file


# Python standard library imports
import os  # Operating system interface, for file and path operations

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_wait(request, friend_id):
    logger.debug(f"remove_friend waiting called for user: {request.user.username}, friend_id: {friend_id}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        
        if not api_user.friends_wait:
            return Response({"error": "You have no friends waiting to remove"}, status=400)
        
        friends_ids = [int(id) for id in api_user.friends_wait.split(',') if id.strip().isdigit()]
        
        if friend_id not in friends_ids:
            return Response({"error": "This user is not in your friends list"}, status=400)
        
        friends_ids.remove(friend_id)
        api_user.friends_wait = ','.join(map(str, friends_ids))
        api_user.save()
        
        return Response({"message": "Friend wait removed successfully"})
    
    except ApiUser.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in remove_friend: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_friends_request(request):
    friend_id = request.data.get('friend_id')
    if not friend_id:
        return Response({"error": "Friend ID is required"}, status=400)

    try:
        # Obtener el usuario amigo (el receptor de la solicitud)
        friend_user = DjangoUser.objects.get(id=friend_id)
        friend_api_user = ApiUser.objects.get(user=friend_user)
        
        # Obtener el usuario que envía la solicitud (usuario autenticado)
        api_user = ApiUser.objects.get(user=request.user)
        
        # Actualizar el campo 'friends_request' del amigo para que contenga el ID del usuario autenticado
        if not friend_api_user.friends_request:
            # Si el campo está vacío, asigna directamente el ID del usuario autenticado
            friend_api_user.friends_request = str(api_user.user.id)  # El usuario autenticado que envía la solicitud
        else:
            # Si ya existen solicitudes, agrega el ID del usuario autenticado si no está presente
            friends_request_list = friend_api_user.friends_request.split(',')
            if str(api_user.user.id) not in friends_request_list:
                friends_request_list.append(str(api_user.user.id))  # Añadir el ID del usuario autenticado
                friend_api_user.friends_request = ','.join(friends_request_list)
            else:
                return Response({"message": "Friend request already sent to this user"}, status=200)
        
        # Guardar los cambios en el usuario amigo
        friend_api_user.save()
        return Response({"message": "Friend request sent successfully"}, status=201)
    
    except DjangoUser.DoesNotExist:
        return Response({"error": "Friend user not found"}, status=404)
    except ApiUser.DoesNotExist:
        return Response({"error": "ApiUser for friend not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)



@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_friends_wait(request):
    friend_id = request.data.get('friend_id')
    if not friend_id:
        return Response({"error": "Friend ID is required"}, status=400)

    try:
        friends_wait = DjangoUser.objects.get(id=friend_id)
        api_user = ApiUser.objects.get(user=request.user)
        
        if not api_user.friends_wait:
            api_user.friends_wait = str(friend_id)
        else:
            friends_wait_list = api_user.friends_wait.split(',')
            if str(friend_id) not in friends_wait_list:
                friends_wait_list.append(str(friend_id))
                api_user.friends_wait = ','.join(friends_wait_list)
            else:
                return Response({"message": "User is already in friends_wait list"}, status=200)
        
        api_user.save()
        return Response({"message": "Friend added to wait list successfully"}, status=201)
    
    except DjangoUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except ApiUser.DoesNotExist:
        return Response({"error": "ApiUser not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_friend(request):
    friend_id = request.data.get('friend_id')
    if not friend_id:
        return Response({"error": "Friend ID is required"}, status=400)

    try:
        friend = DjangoUser.objects.get(id=friend_id)
        api_user = ApiUser.objects.get(user=request.user)
        
        if not api_user.friends:
            api_user.friends = str(friend_id)
        else:
            friends_list = api_user.friends.split(',')
            if str(friend_id) not in friends_list:
                friends_list.append(str(friend_id))
                api_user.friends = ','.join(friends_list)
            else:
                return Response({"message": "User is already a friend"}, status=200)
        
        api_user.save()
        return Response({"message": "Friend added successfully"}, status=201)
    
    except DjangoUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except ApiUser.DoesNotExist:
        return Response({"error": "ApiUser not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_blocked(request, friend_id):
    logger.debug(f"remove_friend called for user: {request.user.username}, friend_id: {friend_id}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        
        if not api_user.friends:
            return Response({"error": "You have no friends blocked to remove"}, status=400)
        
        friends_ids = [int(id) for id in api_user.friends_blocked.split(',') if id.strip().isdigit()]
        
        if friend_id not in friends_ids:
            return Response({"error": "This user is not in your friends list"}, status=400)
        
        friends_ids.remove(friend_id)
        api_user.friends_blocked = ','.join(map(str, friends_ids))
        api_user.save()
        
        return Response({"message": "Friend blocked removed successfully"})
    
    except ApiUser.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in remove_friend: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_friend(request, friend_id):
    logger.debug(f"remove_friend called for user: {request.user.username}, friend_id: {friend_id}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        
        if not api_user.friends:
            return Response({"error": "You have no friends to remove"}, status=400)
        
        friends_ids = [int(id) for id in api_user.friends.split(',') if id.strip().isdigit()]
        
        if friend_id not in friends_ids:
            return Response({"error": "This user is not in your friends list"}, status=400)
        
        friends_ids.remove(friend_id)
        api_user.friends = ','.join(map(str, friends_ids))
        api_user.save()
        
        return Response({"message": "Friend removed successfully"})
    
    except ApiUser.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in remove_friend: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_friends_request(request):
    logger.debug(f"get_friends_request called for user: {request.user.username}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        logger.debug(f"ApiUser found: {api_user}")
        
        if not api_user.friends_request:
            logger.debug("User has no friends request")
            return Response({"friends": []})
        
        logger.debug(f"User's friends_request string: {api_user.friends_request}")
        friends_request_ids = [int(friend_id) for friend_id in api_user.friends_request.split(',') if friend_id.strip().isdigit()]
        logger.debug(f"Parsed friend_request IDs: {friends_request_ids}")
        
        friends_request = DjangoUser.objects.filter(id__in=friends_request_ids).values('id', 'username')
        logger.debug(f"Found friends request: {list(friends_request)}")
        
        return Response({"friends": list(friends_request)})
    
    except ApiUser.DoesNotExist:
        logger.error(f"ApiUser not found for user: {request.user.username}")
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in get_friends_wait: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)



@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_friends_blocked(request):
    logger.debug(f"get_friends_blocked called for user: {request.user.username}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        logger.debug(f"ApiUser found: {api_user}")
        
        if not api_user.friends_blocked:
            logger.debug("User has no friends blocked")
            return Response({"friends": []})
        
        logger.debug(f"User's friends_blocked string: {api_user.friends_blocked}")
        friends_blocked_ids = [int(friend_id) for friend_id in api_user.friends_blocked.split(',') if friend_id.strip().isdigit()]
        logger.debug(f"Parsed friend_blocked IDs: {friends_blocked_ids}")
        
        friends_blocked = DjangoUser.objects.filter(id__in=friends_blocked_ids).values('id', 'username')
        logger.debug(f"Found friends blocked: {list(friends_blocked)}")
        
        return Response({"friends": list(friends_blocked)})
    
    except ApiUser.DoesNotExist:
        logger.error(f"ApiUser not found for user: {request.user.username}")
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in get_friends_wait: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_friends_wait(request):
    logger.debug(f"get_friends_wait called for user: {request.user.username}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        logger.debug(f"ApiUser found: {api_user}")
        
        if not api_user.friends_wait:
            logger.debug("User has no friends waiting")
            return Response({"friends": []})
        
        logger.debug(f"User's friends_wait string: {api_user.friends_wait}")
        friends_wait_ids = [int(friend_id) for friend_id in api_user.friends_wait.split(',') if friend_id.strip().isdigit()]
        logger.debug(f"Parsed friend_wait IDs: {friends_wait_ids}")
        
        friends_wait = DjangoUser.objects.filter(id__in=friends_wait_ids).values('id', 'username')
        logger.debug(f"Found friends waiting: {list(friends_wait)}")
        
        return Response({"friends": list(friends_wait)})
    
    except ApiUser.DoesNotExist:
        logger.error(f"ApiUser not found for user: {request.user.username}")
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in get_friends_wait: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_friends(request, pk):
    print(f"Attempting to fetch friends for user ID: {pk}")
    try:
        django_user = DjangoUser.objects.get(id=pk)
        api_user = ApiUser.objects.get(user=django_user)
        
        friends = api_user.friends
        
        if not friends:
            return Response({"friends": []})
        
        # Si friends es una cadena, la dividimos en una lista
        # Asumiendo que los amigos están separados por comas
        friends_list = [friend.strip() for friend in friends.split(',') if friend.strip()]
        
        return Response({"friends": friends_list})
    except DjangoUser.DoesNotExist:
        print(f"No User found for ID: {pk}")
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except ApiUser.DoesNotExist:
        print(f"No ApiUser found for User ID: {pk}")
        return Response({"error": "ApiUser not found"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_friends(request):
    logger.debug(f"get_user_friends called for user: {request.user.username}")
    try:
        api_user = ApiUser.objects.get(user=request.user)
        logger.debug(f"ApiUser found: {api_user}")
        
        if not api_user.friends:
            logger.debug("User has no friends")
            return Response({"friends": []})
        
        logger.debug(f"User's friends string: {api_user.friends}")
        friends_ids = [int(friend_id) for friend_id in api_user.friends.split(',') if friend_id.strip().isdigit()]
        logger.debug(f"Parsed friend IDs: {friends_ids}")
        
        friends = DjangoUser.objects.filter(id__in=friends_ids).values('id', 'username')
        logger.debug(f"Found friends: {list(friends)}")
        
        return Response({"friends": list(friends)})
    
    except ApiUser.DoesNotExist:
        logger.error(f"ApiUser not found for user: {request.user.username}")
        return Response({"error": "User profile not found"}, status=404)
    except Exception as e:
        logger.exception(f"Unexpected error in get_user_friends: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=500)


