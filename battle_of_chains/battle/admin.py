import logging
import traceback

from django.contrib import admin, messages
from django.contrib.admin.filters import SimpleListFilter
from solo.admin import SingletonModelAdmin

from battle_of_chains.blockchain.tasks import mint_nft_task
from battle_of_chains.utils.mixins import AdminNoChangeMixin

from .forms import AtLeastOneFormSet
from .models import *

logger = logging.getLogger(__name__)


class HasOwnerFilter(SimpleListFilter):
    default_value = 1
    title = 'has owner'
    parameter_name = 'owner__isnull'

    def lookups(self, request, model_admin):
        return (
            ('all', 'All'),
            (0, 'Yes'),
            (1, 'No')
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val:
            if not val.isdigit():
                return queryset
            else:
                return queryset.filter(**{self.parameter_name: int(val)})
        else:
            return queryset.filter(**{self.parameter_name: self.default_value})

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            val = self.value() or str(self.default_value)
            yield {
                'selected': val == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')


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
    list_display = ('id', 'name', 'type', 'level', 'owner', 'date_mod')
    inlines = [ProjectileInline]
    actions = ('mint_nft',)
    list_filter = (HasOwnerFilter, 'type', 'basic_free_tank', 'for_sale', 'origin_offer')
    readonly_fields = ('origin_offer',)
    search_fields = ('owner__email', 'id')

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


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(BattleSettings)
class BattleSettingsAdmin(SingletonModelAdmin):
    pass
