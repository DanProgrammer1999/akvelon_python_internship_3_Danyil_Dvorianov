from django.contrib import admin

from transapp.models.agent import Agent
from transapp.models.transaction import Transaction

# Register your models here.

admin.site.register(Agent)
