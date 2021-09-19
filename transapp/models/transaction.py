from django.db import models
from .agent import Agent


class Transaction(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    # store integer instead of float to avoid float representation problems
    amount = models.IntegerField()
    date = models.DateTimeField()
