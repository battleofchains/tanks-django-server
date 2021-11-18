from django.db import models
from battle_of_chains.users.models import User


class Room(models.Model):
    users = models.ManyToManyField(to=User, related_name='rooms')

    @property
    def name(self):
        return f"room_{self.pk}"

    def __str__(self):
        return self.name
