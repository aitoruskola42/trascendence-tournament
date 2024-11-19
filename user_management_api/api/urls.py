# Django imports
from django.urls import path  # Used for URL routing

# Local imports
from . import views  # Various view modules

urlpatterns = [
    path('matches4/<int:pk>/', views.match4_list_id, name='match4_list_id'),
    path('matches/<int:pk>/', views.match_list_id, name='match_list_id'),
    path('matches2/stats_view/<int:user_id>/', views.stats_view, name='stats_view'),
]
