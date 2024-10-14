# Django imports
from django.urls import path  # Used for URL routing

# Django Rest Framework and Simple JWT imports
from rest_framework_simplejwt.views import TokenRefreshView  # View for refreshing JWT tokens

# Local imports
from .views import user_views, avatar_views, friends_views, logout, two_factor_views,  tournaments_views, matches_views  # Various view modules
from .oauth2_views import create_oauth2_app  # OAuth2 application creation view
from .custom_jwt import CustomTokenObtainPairView  # Custom JWT token obtain view
from . import oauth42  # OAuth2 related module
from .views.user_views import logout 

from django.urls import path


urlpatterns = [
    # Rutas para torneos regulares
    path('tournaments/ready/', tournaments_views.tournament_ready_list, name='tournament_ready_list'),
    path('tournaments/open/', tournaments_views.tournament_open_list, name='tournament_open_list'),
    path('tournaments/', tournaments_views.tournament_list, name='tournament_list'),
    path('tournaments/user/', tournaments_views.user_tournaments, name='user_tournaments'),
    path('tournaments/creator/<int:creator_id>/', tournaments_views.get_creator_info, name='get_creator_info'),
    path('tournaments/create/', tournaments_views.create_tournament, name='create_tournament'),
    path('tournaments/<int:pk>/', tournaments_views.tournament_detail, name='tournament_detail'),
    path('tournaments/<int:pk>/join/', tournaments_views.join_tournament, name='join_tournament'),
    path('tournaments/<int:pk>/start/', tournaments_views.start_tournament, name='start_tournament'),
    path('tournaments/<int:pk>/end/', tournaments_views.end_tournament, name='end_tournament'),

    # Rutas para partidas 1 vs 1
    path('one-vs-one/create/', tournaments_views.create_one_vs_one_match, name='create_one_vs_one_match'),
    path('one-vs-one/', tournaments_views.get_one_vs_one_matches, name='get_one_vs_one_matches'),
]

urlpatterns += [
    path('matches/', matches_views.match_list, name='match_list'),
    path('matches/<int:pk>/', matches_views.match_detail, name='match_detail'),
    path('matches/<int:pk>/start/', matches_views.start_match, name='start_match'),
    path('matches/<int:match_pk>/games/<int:game_pk>/point/', matches_views.record_point, name='record_point'),
    path('matches/<int:match_pk>/games/<int:game_pk>/pause/', matches_views.pause_game, name='pause_game'),
    path('matches/<int:match_pk>/games/<int:game_pk>/resume/', matches_views.resume_game, name='resume_game'),
    path('matches/<int:match_pk>/games/<int:game_pk>/events/', matches_views.game_events, name='game_events'),
]

urlpatterns += [
    path("users/", user_views.get_users, name="get_users"),
    path("users/<int:pk>/", user_views.get_user, name="get_user"),
    path("users/create/", user_views.create_user, name="create_user"),
    path('users/login/', user_views.login_user, name='login'),
    path('users/signout/', user_views.sign_out_user, name='signout'),
    path("users/profile/<int:pk>/", user_views.get_user_profile, name="get_user_profile"),
    path("users/profile/", user_views.get_user_profile, name="get_user_profile"),
    path("friends/", friends_views.get_friends, name="get_friends"),
    path("users/update/<int:pk>/", user_views.update_user_profile, name="update_user_profile"),
    path("users/change-password/", user_views.change_password, name="change_password"),
    path('users/upload-avatar/', avatar_views.upload_avatar, name='upload_avatar'),
    path('users/avatar/<int:user_id>/', avatar_views.get_avatar, name='get_avatar'),
    path('default-avatar/', avatar_views.get_default_avatar, name='get_default_avatar'),
    path('create_oauth2_app/', create_oauth2_app, name='create_oauth2_app'),
    path('oauth/login/', oauth42.auth_login, name='oauth_login'),
    path('oauth/callback/', oauth42.auth_callback, name='oauth_callback'),
    path('oauth/user_info/', oauth42.get_user_info, name='user_info'),
    path('protected/',  user_views.protected_view, name='protected_view'),
    path('oauth/logout/', oauth42.auth_logout, name='oauth_logout'),
    path('check-auth/', user_views.check_auth, name='check_auth'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('test-token/', user_views.test_token, name='test_token'),
    path('logout/', user_views.logout_view, name='auth_logout'),
    path('enable-2fa/', two_factor_views.enable_2fa, name='enable_2fa'),
    path('verify-2fa/', two_factor_views.verify_2fa, name='verify_2fa'),
    path('disable-2fa/', two_factor_views.disable_2fa, name='disable_2fa'),
    path('oauth-2fa-verify/', oauth42.oauth_verify_2fa, name='oauth_2fa_verify'),
    path('users/update-profile/', user_views.update_user_profile, name='update_user_profile'),
    path('users/list/', user_views.get_user_list, name='user_list'),
    path('friends/get_user_friends/', friends_views.get_user_friends, name='get_user_friends'),
    path('friends/get_friends_wait/', friends_views.get_friends_wait, name='get_friends_wait'),
    path('friends/get_friends_blocked/', friends_views.get_friends_blocked, name='get_friends_blocked'),
    path('friends/get_friends_request/', friends_views.get_friends_request, name='get_friends_request'),
    path('friends/remove/<int:friend_id>/', friends_views.remove_friend, name='remove_friend'),
    path('friends/remove-blocked/<int:friend_id>/', friends_views.remove_blocked, name='remove_bloked'),
    path('friends/remove-wait/<int:friend_id>/', friends_views.remove_wait, name='remove_wait'),
    path('friends/add/', friends_views.add_friend, name='add_friend'),
    path('friends/add_final/', friends_views.add_friend_final, name='add_friend_final'),
    path('friends/add_friends_wait/', friends_views.add_friends_wait, name='add_friends_wait'),
    path('friends/add_friends_request/', friends_views.add_friends_request, name='add_friends_request'),
    path('friends/remove-request/<int:friend_id>/', friends_views.remove_request, name='remove_request'),
    path('users/<int:user_id>/participations/', user_views.get_user_participations, name='get_user_participations'),
    path('users/<int:user_id>/tournaments/', user_views.user_tournaments, name='user_tournaments'),
]

