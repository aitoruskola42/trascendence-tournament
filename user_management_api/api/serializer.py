# Django imports
from django.contrib.auth import login, get_user_model, authenticate  # Authentication functions
from django.contrib.auth.models import User as DjangoUser  # Django's built-in User model

# Django Rest Framework imports
from rest_framework import serializers  # Serialization framework for REST APIs

# Local imports
from .models import ApiUser  # Custom User models
from .models import Tournament, Participation, Match, Game, GameEvent, ApiUser
User = get_user_model()  # Get the active User model


class ParticipantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
  #  display_name = serializers.CharField(source='user.display_name')

    class Meta:
        model = Participation
        fields = ['id', 'display_name', 'score']

class ParticipationSerializer(serializers.ModelSerializer):
    user = ParticipantSerializer(read_only=True)

    class Meta:
        model = Participation
        fields = ['id', 'user', 'tournament', 'score']  # Ajusta estos campos según tu modelo


class TournamentOpenSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    current_participants = serializers.SerializerMethodField()
    can_start = serializers.SerializerMethodField()
    creator = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'start_date', 'status', 'tournament_type', 'creator', 'max_participants', 'participants', 'current_participants', 'can_start']

    def get_participants(self, obj):
        participations = Participation.objects.filter(tournament=obj.id)
        return ParticipantSerializer(participations, many=True).data

    def get_current_participants(self, obj):
        return Participation.objects.filter(tournament=obj.id).count()

    def get_can_start(self, obj):
        return obj.status == 'REGISTRATION' and self.get_current_participants(obj) >= 2


    def create(self, validated_data):
        creator_id = self.context['request'].user.apiuser.id
        tournament = Tournament.objects.create(creator=creator_id, **validated_data)
        display_name = self.context['request'].user.apiuser.display_name
        # Crear la participación para el creador del torneo
        Participation.objects.create(
            user=self.context['request'].user.apiuser,
            tournament=tournament,
            score=0,
            display_name=display_name,
        )

        return tournament

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['creator'] = instance.creator  # Asegúrate de que el creator se incluya en la representación
        return data

class TournamentSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    current_participants = serializers.SerializerMethodField()
    can_start = serializers.SerializerMethodField()
    creator = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'start_date', 'status', 'tournament_type', 'creator', 'max_participants', 'participants', 'current_participants', 'can_start']

    def get_participants(self, obj):
        participations = Participation.objects.filter(tournament=obj.id)
        return ParticipantSerializer(participations, many=True).data

    def get_current_participants(self, obj):
        return Participation.objects.filter(tournament=obj.id).count()

    def get_can_start(self, obj):
        return obj.status == 'REGISTRATION' and self.get_current_participants(obj) >= 2


    def create(self, validated_data):
        creator_id = self.context['request'].user.apiuser.id
        tournament = Tournament.objects.create(creator=creator_id, **validated_data)
        display_name = self.context['request'].user.apiuser.display_name
        # Crear la participación para el creador del torneo
        Participation.objects.create(
            user=self.context['request'].user.apiuser,
            tournament=tournament,
            score=0,
            display_name=display_name,
        )

        return tournament

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['creator'] = instance.creator  # Asegúrate de que el creator se incluya en la representación
        return data

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'

class GameEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameEvent
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ApiUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    display_name = serializers.CharField(required=False)
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

        display_name = validated_data.get('display_name', validated_data['username'])

        api_user = ApiUser.objects.create(
            user=django_user,
            display_name=display_name,
            friends=validated_data.get('friends', ''),
            friends_wait=validated_data.get('friends_wait', ''),
            friends_request=validated_data.get('friends_request', ''),
            friends_blocked=validated_data.get('friends_blocked', ''),
            user_42=validated_data.get('user_42', False),   
            oauth_id=validated_data.get('oauth_id', '')
        )
        
        return api_user