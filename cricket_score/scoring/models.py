from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_batsman = models.BooleanField(default=True)
    is_bowler = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.team.name})"


class Match(models.Model):
    STATUS_CHOICES = (
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
    )
    team1 = models.ForeignKey(Team, related_name="team1", on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name="team2", on_delete=models.CASCADE)
    overs = models.IntegerField()
    current_inning = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ongoing')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.team1} vs {self.team2}"


class BallByBall(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    over = models.IntegerField()
    ball = models.IntegerField()
    batsman = models.ForeignKey(Player, related_name="batsman", on_delete=models.CASCADE)
    bowler = models.ForeignKey(Player, related_name="bowler", on_delete=models.CASCADE)
    runs = models.IntegerField(default=0)
    is_wicket = models.BooleanField(default=False)

    def __str__(self):
        return f"Over {self.over}.{self.ball} - {self.runs} runs"
