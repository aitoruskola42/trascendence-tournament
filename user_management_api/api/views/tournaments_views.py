from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ..models import Tournament, Match, ApiUser
from ..serializer import MatchSerializer
from django.db import models
from django.db.models import Count, F
from django.db.models.functions import Coalesce


