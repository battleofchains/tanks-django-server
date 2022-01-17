from django.contrib import admin

from battle_of_chains.battle.models import Tank

from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'amount', 'amount_sold', 'is_active')

    def amount_sold(self, instance):
        return Tank.objects.filter(offer=instance, nft__isnull=False).count()
