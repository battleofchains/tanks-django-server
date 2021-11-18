from django.contrib import admin

from battle_of_chains.utils.mixins import AdminNoChangeMixin

from .models import *


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


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


@admin.register(WeaponType)
class WeaponTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color')


@admin.register(Weapon)
class WeaponAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'owner', 'tank')
