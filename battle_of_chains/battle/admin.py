from django.contrib import admin

from battle_of_chains.utils.mixins import AdminNoChangeMixin

from .models import *


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
    extra = 0


@admin.register(Tank)
class TankAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'level', 'owner')
    inlines = [ProjectileInline]


@admin.register(ProjectileType)
class ProjectileTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color')


@admin.register(Projectile)
class Projectile(admin.ModelAdmin):
    list_display = ('id', 'type', 'tank')
