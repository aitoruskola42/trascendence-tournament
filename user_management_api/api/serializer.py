from rest_framework import serializers  # Serialization framework for REST APIs

from .models import Match

class MatchSerializer(serializers.ModelSerializer):
    match_type_display = serializers.CharField(source='get_match_type_display', read_only=True)

    class Meta:
        model = Match
        fields = [
            'id',
            'match_type',
            'match_type_display',
            'tournament_id',
            'player1_id',
            'player2_id',
            'player1_display_name',
            'player2_display_name',
            'player1_score',
            'player2_score',
            'winner_id',
            'date'
        ]
    
    def validate(self, data):
        if data.get('match_type') == 'INDIVIDUAL' and data.get('tournament_id') != 0:
            raise serializers.ValidationError("Las partidas individuales deben tener tournament_id igual a 0.")
        return data

    def create(self, validated_data):
        if validated_data.get('match_type') == 'INDIVIDUAL':
            validated_data['tournament_id'] = 0
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('match_type') == 'INDIVIDUAL':
            validated_data['tournament_id'] = 0
        return super().update(instance, validated_data)




