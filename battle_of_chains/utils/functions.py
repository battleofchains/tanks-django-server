import random

from battle_of_chains.battle.models import Projectile, ProjectileType, Tank, TankType
from battle_of_chains.users.models import User


def generate_first_squad(instance: User):
    tank_types = TankType.objects.all()
    projectile_types = ProjectileType.objects.all()
    if tank_types.count() == 0 or projectile_types.count() == 0:
        return
    tank_types = tuple(tank_types)
    for i in range(3):
        tank_type = random.choice(tank_types)
        tank = Tank.objects.create(type=tank_type, owner=instance,
                                   hp=tank_type.hp_step,
                                   moving_price=tank_type.moving_price_default,
                                   damage_bonus=tank_type.damage_bonus_default,
                                   critical_chance=tank_type.critical_chance_default,
                                   overlook=tank_type.overlook_default,
                                   armor=tank_type.armor_default,
                                   block_chance=tank_type.block_chance_default)

        p_types = tuple(projectile_types.filter(tank_types=tank_type))
        for projectile_type in p_types:
            Projectile.objects.create(type=projectile_type, tank=tank,
                                      avg_damage=projectile_type.avg_damage_default,
                                      ricochet_chance=projectile_type.ricochet_chance_default,
                                      distance=projectile_type.distance_default,
                                      environment_damage=projectile_type.environment_damage_default,
                                      critical_hit_bonus=projectile_type.critical_hit_bonus_default,
                                      radius=projectile_type.radius_default,
                                      fire_price=projectile_type.fire_price_default)
