from django.db import models
from .agent import Agent


class Transaction(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField()
