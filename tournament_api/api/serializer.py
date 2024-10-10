# Django imports
from django.contrib.auth import login, get_user_model, authenticate  # Authentication functions
from django.contrib.auth.models import User as DjangoUser  # Django's built-in User model

# Django Rest Framework imports
from rest_framework import serializers  # Serialization framework for REST APIs

# Local imports
from .models import ApiUser, User  # Custom User models
User = get_user_model()  # Get the active User model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ApiUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    display_name = serializers.CharField(allow_blank=True, required=False)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    friends = serializers.CharField(allow_blank=True, required=False)
    friends_wait = serializers.CharField(allow_blank=True, required=False)
    friends_request = serializers.CharField(allow_blank=True, required=False)
    friends_blocked = serializers.CharField(allow_blank=True, required=False)
    user_42 = serializers.BooleanField(required=False)
    oauth_id = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = ApiUser
        fields = [
            'username', 'email', 'password', 'display_name', 'first_name', 'last_name',
            'friends', 'friends_wait', 'friends_request', 'friends_blocked',
            'user_42', 'oauth_id'
        ]

    def create(self, validated_data):
        user_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            
        }
        password = validated_data['password']
        django_user = DjangoUser.objects.create_user(**user_data, password=password)
        api_user = ApiUser.objects.create(
            user=django_user,
            display_name = validated_data['username'],
            friends=validated_data.get('friends', ''),
            friends_wait=validated_data.get('friends_wait', ''),
            friends_request=validated_data.get('friends_request', ''),
            friends_blocked=validated_data.get('friends_blocked', ''),
            user_42=validated_data.get('user_42', False),   
            oauth_id=validated_data.get('oauth_id', '')
        )
        
        return api_user