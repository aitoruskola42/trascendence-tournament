from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.utils import timezone
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ApiUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    avatar_image = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/default.jpg')
    friends = models.CharField(max_length=200, blank=True, null=True)
    friends_wait = models.CharField(max_length=200, blank=True, null=True)
    friends_request = models.CharField(max_length=200, blank=True, null=True)
    friends_blocked = models.CharField(max_length=200, blank=True, null=True)
    user_42 = models.BooleanField(default=False)
    oauth_id = models.CharField(max_length=200, blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    two_factor_configured = models.BooleanField(default=False)
    tournaments = models.ManyToManyField('Tournament', related_name='participants', blank=True)
    participated_tournaments = models.ManyToManyField('Tournament', related_name='api_participants', blank=True)

    def __str__(self):
        return self.display_name

    def get_full_user_data(self):
        return {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'friends': self.friends,
            'friends_wait': self.friends_wait,
            'friends_request': self.friends_request,
            'friends_blocked': self.friends_blocked,
            'user_42': self.user_42,
            'oauth_id': self.oauth_id,
            'date_joined': timezone.localtime(self.user.date_joined).isoformat(),
            'last_login': timezone.localtime(self.user.last_login).isoformat() if self.user.last_login else None,
            'two_factor_enabled': self.two_factor_enabled,
            'two_factor_configured': self.two_factor_configured,
            'avatar_image': self.avatar_image.url if self.avatar_image else None,
            'display_name': self.display_name,
        }


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('REGISTRATION', 'Registration'),
        ('IN_PROGRESS', 'In Progress'),
        ('FINISHED', 'Finished')
    ], default='REGISTRATION')
    tournament_type = models.CharField(max_length=20)
    creator = models.IntegerField(default=0)
    max_participants = models.IntegerField(default=0)
    # No necesitamos definir 'participants' aquí, ya que está definido en ApiUser

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_one_vs_one_tournament(cls):
        one_vs_one, created = cls.objects.get_or_create(
            tournament_type='ONE_VS_ONE',
            defaults={
                'name': '1 vs 1 Matches',
                'status': 'ALWAYS_OPEN',
                'creator': DjangoUser.objects.get(username='admin')
            }
        )
        return one_vs_one


class Participation(models.Model):
    user = models.ForeignKey(ApiUser, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    display_name = models.CharField(max_length=200, blank=True, null=True)    

    class Meta:
        unique_together = ['tournament', 'user']

    def __str__(self):
        return f"{self.user.display_name} in {self.tournament.name}"




class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    player1 = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='matches_as_player1')
    player2 = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='matches_as_player2')
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    winner = models.ForeignKey(Participation, on_delete=models.SET_NULL, null=True, related_name='matches_won')
    round = models.IntegerField(default=1)
    order = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.player1.alias} vs {self.player2.alias} - {self.tournament.name}"

    @classmethod
    def create_one_vs_one_match(cls, player1, player2):
        one_vs_one_tournament = Tournament.get_or_create_one_vs_one_tournament()
        return cls.objects.create(
            tournament=one_vs_one_tournament,
            player1=player1,
            player2=player2,
            round='FINAL',
            order=1
        )


class Game(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='games')
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    winner = models.ForeignKey(Participation, on_delete=models.SET_NULL, null=True, related_name='games_won')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Game in {self.match} - {self.player1_score}:{self.player2_score}"


class GameEvent(models.Model):
    EVENT_TYPES = [
        ('POINT', 'Point Scored'),
        ('PAUSE', 'Game Paused'),
        ('RESUME', 'Game Resumed'),
        ('END', 'Game Ended')
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    player = models.ForeignKey(Participation, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.event_type} in {self.game} at {self.timestamp}"


@receiver(post_migrate)
def create_one_vs_one_tournament(sender, **kwargs):
    if sender.name == 'tournament_api':  # Reemplaza con el nombre de tu app
        Tournament.get_or_create_one_vs_one_tournament()


@receiver(post_save, sender=Tournament)
def ensure_creator_is_participant(sender, instance, created, **kwargs):
    if created and instance.creator:
        instance.participants.add(instance.creator)