from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.utils import timezone
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tournament(models.Model):
    start_date = models.DateTimeField()
    winner_id = models.IntegerField(default=0)

    def __str__(self):
        return f"Tournament {self.id} - Started on {self.start_date}"

class Match(models.Model):
    MATCH_TYPES = [
        ('INDIVIDUAL', 'Partida Individual'),
        ('SEMIFINAL', 'Semifinal de Torneo'),
        ('FINAL', 'Final de Torneo'),
    ]

    match_type = models.CharField(max_length=20, choices=MATCH_TYPES)
    tournament_id = models.IntegerField(default=0)  # 0 para partidas individuales
    player1_id = models.IntegerField()
    player2_id = models.IntegerField()
    player1_display_name = models.CharField(max_length=100)
    player2_display_name = models.CharField(max_length=100)
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    winner_id = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.tournament_id != 0:
            return f"{self.get_match_type_display()} - Torneo {self.tournament_id}: {self.player1_display_name} vs {self.player2_display_name}"
        return f"Partida Individual: {self.player1_display_name} vs {self.player2_display_name}"

    def save(self, *args, **kwargs):
        if self.match_type == 'INDIVIDUAL':
            self.tournament_id = 0
        super().save(*args, **kwargs)

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


  