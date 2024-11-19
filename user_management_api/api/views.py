from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from . import views_match_history

@api_view(['GET'])
def stats_view(request, user_id):
    try:
        return views_match_history.stats_view(request, user_id)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def match_list_id(request, pk):
    try:
        return views_match_history.match_list_id(request, pk)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def match4_list_id(request, pk):
    try:
        return views_match_history.match4_list_id(request, pk)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
