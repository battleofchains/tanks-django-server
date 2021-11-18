from django.db import models


class Wallet(models.Model):
    address = models.CharField(max_length=42, verbose_name='Wallet address', primary_key=True)
    date_add = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Last update')

    def __str__(self):
        return self.address
