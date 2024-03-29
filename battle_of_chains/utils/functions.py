import random

from battle_of_chains.battle.models import Tank
from battle_of_chains.users.models import User


def generate_first_squad(instance: User):
    basic_tanks = Tank.objects.filter(basic_free_tank=True)
    if basic_tanks.count() == 0:
        return
    basic_tanks = list(basic_tanks)
    for i in range(3):
        if len(basic_tanks) > 0:
            random.shuffle(basic_tanks)
            basic_tank = basic_tanks.pop()
            projectiles = tuple(basic_tank.projectiles.all())
            tank = basic_tank
            tank.pk = None
            tank.owner = instance
            tank.basic_free_tank = False
            tank.save()
            for projectile in projectiles:
                projectile.pk = None
                projectile.tank = tank
                projectile.save()
