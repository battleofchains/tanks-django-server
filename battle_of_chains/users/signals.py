import random

from django.db.models.signals import post_save
from django.dispatch import receiver

from battle_of_chains.battle.models import Squad, Tank, TankType, Weapon, WeaponType

from .models import User


@receiver(post_save, sender=User)
def create_first_squad(sender, instance, created, **kwargs):
    if created:
        tank_types = TankType.objects.all()
        weapon_types = WeaponType.objects.all()
        if tank_types.count() == 0 or weapon_types.count() == 0:
            return
        tank_types = tuple(tank_types)
        squad = Squad.objects.create(owner=instance, name='First squad')
        for i in range(5):
            tank_type = random.choice(tank_types)
            tank = Tank.objects.create(type=tank_type, owner=instance, squad=squad,
                                       hp=tank_type.hp_step,
                                       action_points=tank_type.action_points_default,
                                       moving_points=tank_type.moving_points_default,
                                       damage_bonus=tank_type.damage_bonus_default,
                                       critical_chance=tank_type.critical_chance_default,
                                       overlook=tank_type.overlook_default,
                                       armor=tank_type.armor_default,
                                       block_chance=tank_type.block_chance_default,
                                       fuel=tank_type.fuel_default)

            w_types = tuple(weapon_types.filter(tank_types__in=tank_type))
            for w in range(tank_type.max_weapons):
                weapon_type = random.choice(w_types)
                Weapon.objects.create(owner=instance, type=weapon_type, tank=tank,
                                      max_damage=weapon_type.max_damage_default,
                                      min_damage=weapon_type.min_damage_default,
                                      distance=weapon_type.distance_default,
                                      environment_damage=weapon_type.environment_damage_default,
                                      critical_hit_bonus=weapon_type.critical_hit_bonus_default,
                                      usage_limit=weapon_type.usage_limit_default)
