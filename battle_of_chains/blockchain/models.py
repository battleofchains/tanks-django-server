from django.db import models

from battle_of_chains.battle.models import Tank


class Wallet(models.Model):
    address = models.CharField(max_length=50, verbose_name='Wallet address', primary_key=True)
    date_add = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Last update')

    def __str__(self):
        return self.address


class NFT(models.Model):
    address = models.CharField(max_length=50, primary_key=True)
    tank = models.OneToOneField(Tank, on_delete=models.SET_NULL, null=True)
    for_sale = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=15, decimal_places=6)
