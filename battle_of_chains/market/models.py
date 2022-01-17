from django.db import models

from battle_of_chains.battle.models import Tank


class Offer(models.Model):
    title = models.CharField(max_length=100)
    base_tank = models.ForeignKey(Tank, on_delete=models.CASCADE, related_name='offers')
    amount = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=6, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
