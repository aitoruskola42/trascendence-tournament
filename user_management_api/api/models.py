from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.utils import timezone
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth import get_user_model



class Match(models.Model):
    MATCH_TYPES = [
        ('INDIVIDUAL', 'INDIVIDUAL'),
        ('SEMIFINAL', 'SEMIFINAL'),
        ('FINAL', 'FINAL'),
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

