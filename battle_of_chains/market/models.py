from django.db import models

from battle_of_chains.battle.models import Tank


class Offer(models.Model):
    title = models.CharField(max_length=100)
    base_tank = models.OneToOneField(Tank, on_delete=models.CASCADE, related_name='offer')
    amount = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=6, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def amount_sold(self):
        return Tank.objects.filter(origin_offer=self, nft__isnull=False).count()

    @property
    def amount_left(self):
        return self.amount - Tank.objects.filter(origin_offer=self, nft__isnull=False).count()

    def save(self, *args, **kwargs):
        super(Offer, self).save(*args, **kwargs)
        self.base_tank.save()  # to update Tank.date_add field for marketplace logic


class Banner(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField()
    link = models.URLField()
    date_add = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
