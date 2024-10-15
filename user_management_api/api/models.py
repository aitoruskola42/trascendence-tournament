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




class Match2(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches_2_players')
    player1 = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='matches_2p_player1')
    player2 = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='matches_2p_player2')
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    winner = models.ForeignKey(Participation, on_delete=models.SET_NULL, null=True, related_name='matches_2p_won')
    round = models.IntegerField(default=1)
    order = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.player1.display_name} vs {self.player2.display_name} - {self.tournament.name}"

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



class Match4(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches_4_players')
    player1 = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='matches_4p_player1')
    player2 = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='matches_4p_player2')
    player3 = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='matches_4p_player3')
    player4 = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='matches_4p_player4')
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    player3_score = models.IntegerField(default=0)
    player4_score = models.IntegerField(default=0)
    winner = models.ForeignKey(Participation, on_delete=models.SET_NULL, null=True, related_name='matches_4p_won')
    round = models.IntegerField(default=1)
    order = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('FINISHED', 'Finished')
    ], default='PENDING')

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.player1.display_name} vs {self.player2.display_name} vs {self.player3.display_name} vs {self.player4.display_name} - {self.tournament.name}"

    @classmethod
    def create_four_player_match(cls, tournament, player1, player2, player3, player4, round_num, order):
        return cls.objects.create(
            tournament=tournament,
            player1=player1,
            player2=player2,
            player3=player3,
            player4=player4,
            round=round_num,
            order=order
        )
    

    def is_finished(self):
        # Implementa la lógica para determinar si el partido ha terminado
        # Por ejemplo, si algún jugador ha alcanzado cierta puntuación
        return max(self.player1_score, self.player2_score, self.player3_score, self.player4_score) >= 10

    def determine_winner(self):
        scores = [
            (self.player1, self.player1_score),
            (self.player2, self.player2_score),
            (self.player3, self.player3_score),
            (self.player4, self.player4_score)
        ]
        self.winner = max(scores, key=lambda x: x[1])[0]