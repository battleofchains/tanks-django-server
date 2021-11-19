from django.contrib import admin

from battle_of_chains.utils.mixins import AdminNoChangeMixin

from .models import *


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(BattleType)
class BattleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'players_number')


@admin.register(Battle)
class BattleAdmin(AdminNoChangeMixin, admin.ModelAdmin):
    list_display = ('id', 'map', 'created', 'status')


@admin.register(Squad)
class SquadAdmin(AdminNoChangeMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'owner')


@admin.register(TankType)
class TankTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Tank)
class TankAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'level', 'owner')


@admin.register(ProjectileType)
class ProjectileTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color')


@admin.register(Projectile)
class Projectile(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'owner', 'tank')
