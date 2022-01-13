import logging
import traceback

from django.contrib import admin, messages

from battle_of_chains.blockchain.tasks import mint_nft_task
from battle_of_chains.utils.mixins import AdminNoChangeMixin

from .forms import AtLeastOneFormSet
from .models import *

logger = logging.getLogger(__name__)


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(BattleType)
class BattleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'players_number', 'player_tanks_number')


@admin.register(Battle)
class BattleAdmin(AdminNoChangeMixin, admin.ModelAdmin):
    list_display = ('id', 'map', 'created', 'status')


@admin.register(TankType)
class TankTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ProjectileInline(admin.TabularInline):
    model = Projectile
    extra = 1
    formset = AtLeastOneFormSet


@admin.register(Tank)
class TankAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'level', 'owner')
    inlines = [ProjectileInline]
    actions = ('mint_nft',)
    list_filter = ('type', 'basic_free_tank', 'for_sale')

    def mint_nft(self, request, queryset):
        for obj in queryset:
            try:
                mint_nft_task(obj.id)
                self.message_user(request, f"NFT for tank {obj} is minting", level=messages.INFO)
            except Exception as e:
                self.message_user(request, f"Error occurred while trying to mint {obj}: {e} ", level=messages.ERROR)
                logger.error(traceback.format_exc())


@admin.register(ProjectileType)
class ProjectileTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color')


@admin.register(Projectile)
class Projectile(admin.ModelAdmin):
    list_display = ('id', 'type', 'tank')
