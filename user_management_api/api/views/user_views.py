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
