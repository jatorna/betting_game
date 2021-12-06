from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    address = models.CharField(max_length=200)
    bets = models.IntegerField(default=0)


class CurrentBet(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64)
    amount = models.IntegerField(default=0)
    holdId = models.CharField(max_length=64, default=0)
