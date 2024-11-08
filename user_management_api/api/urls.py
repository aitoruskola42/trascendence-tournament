# Django imports
from django.urls import path  # Used for URL routing

# Django Rest Framework and Simple JWT imports
from rest_framework_simplejwt.views import TokenRefreshView  # View for refreshing JWT tokens

# Local imports
from . import views  # Various view modules

urlpatterns = [
    path('matches2/register-tournament/', views.register_tournament, name='register_tournament'),
    path('matches2/game-results/', views.game_result, name='game_result'),
    path('matches4/<int:pk>/', views.match4_list_id, name='match4_list_id'),
    path('matches/<int:pk>/', views.match_list_id, name='match_list_id'),
    path('matches2/semifinal-winners/<int:tournament_id>/', views.semifinal_winners, name='semifinal_winners'),
    path('matches2/end-tournament/<int:tournament_id>/', views.end_tournament, name='end_tournament'),
    path('matches2/stats_view/<int:user_id>/', views.stats_view, name='stats_view'),
    path('matches/', views.match_list, name='match_list'),
    path('matches4/', views.match4_list, name='match4_list')
]

