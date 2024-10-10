# Django imports
from django.contrib.auth import authenticate  # Handles user authentication
from django.contrib.auth.models import User as DjangoUser  # Django's built-in User model
from django.contrib.auth.decorators import login_required  # Decorator to restrict access to logged-in users
from django.conf import settings  # Access to Django project settings
from django.http import HttpResponse, JsonResponse  # HTTP response classes
from django.shortcuts import redirect  # Function for redirecting to a specific URL

# Django Rest Framework imports
from rest_framework.decorators import api_view, authentication_classes, permission_classes  # Decorators for API views
from rest_framework.response import Response  # REST framework's Response class
from rest_framework import status  # Provides HTTP status codes
from rest_framework.authentication import TokenAuthentication  # Token-based authentication
from rest_framework.authtoken.models import Token  # Token model for authentication
from rest_framework.permissions import IsAuthenticated  # Permission class to ensure user is authenticated

# Simple JWT imports
from rest_framework_simplejwt.tokens import RefreshToken  # Handles refresh tokens for JWT

# Python standard library imports
    import os  # Operating system interface, for file and path operations

# Third-party library imports
import requests  # HTTP library for making requests

# Local imports
from .models import User, ApiUser  # Custom User and ApiUser models
from .serializer import UserSerializer, ApiUserSerializer  # Serializers for User and ApiUser models

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.pk,
            'username': user.username,
            'aitor': 'hola'
        })
    return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)