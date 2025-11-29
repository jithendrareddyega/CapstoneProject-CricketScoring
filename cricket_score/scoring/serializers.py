from rest_framework import serializers
from .models import Match, Team, Player, BallByBall

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class BallByBallSerializer(serializers.ModelSerializer):
    class Meta:
        model = BallByBall
        fields = '__all__'
