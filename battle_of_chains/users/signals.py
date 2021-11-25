import random

from django.db.models.signals import post_save
from django.dispatch import receiver

from battle_of_chains.battle.models import Projectile, ProjectileType, Squad, Tank, TankType

from .models import User


def generate_first_squad(instance):
    tank_types = TankType.objects.all()
    projectile_types = ProjectileType.objects.all()
    if tank_types.count() == 0 or projectile_types.count() == 0:
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

        p_types = tuple(projectile_types.filter(tank_types=tank_type))
        for w in range(tank_type.max_projectiles):
            projectile_type = random.choice(p_types)
            Projectile.objects.create(owner=instance, type=projectile_type, tank=tank,
                                      avg_damage=projectile_type.avg_damage_default,
                                      ricochet_chance=projectile_type.ricochet_chance_default,
                                      distance=projectile_type.distance_default,
                                      environment_damage=projectile_type.environment_damage_default,
                                      critical_hit_bonus=projectile_type.critical_hit_bonus_default,
                                      usage_limit=projectile_type.usage_limit_default,
                                      radius=projectile_type.radius_default)


@receiver(post_save, sender=User)
def create_first_squad(sender, instance, created, **kwargs):
    if created:
        generate_first_squad(instance)
