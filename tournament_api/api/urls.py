# Django imports
from django.urls import path  # Used for URL routing

# Django Rest Framework and Simple JWT imports
from rest_framework_simplejwt.views import TokenRefreshView  # View for refreshing JWT tokens

# Local imports
from .views import user_views, avatar_views, friends_views, logout, two_factor_views  # Various view modules
from .oauth2_views import create_oauth2_app  # OAuth2 application creation view
from .custom_jwt import CustomTokenObtainPairView  # Custom JWT token obtain view
from . import oauth42  # OAuth2 related module

urlpatterns = [
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
    path('friends/add_friends_wait/', friends_views.add_friends_wait, name='add_friends_wait'),
    path('friends/add_friends_request/', friends_views.add_friends_request, name='add_friends_request'),







]

