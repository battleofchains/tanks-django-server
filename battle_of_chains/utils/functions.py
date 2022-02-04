import random

from battle_of_chains.battle.models import Tank
from battle_of_chains.market.models import Offer
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


def create_tank_from_offer(offer: Offer) -> Tank:
    base_tank = offer.base_tank
    props = {k: v for k, v in base_tank.__dict__.items() if not k.startswith('_') and k not in
             ('id', 'owner_id', 'price', 'basic_free_tank', 'origin_offer_id', 'date_mod')}
    props['price'] = offer.price
    props['origin_offer_id'] = offer.id
    tank = Tank.objects.create(**props)
    for projectile in base_tank.projectiles.all():
        projectile.pk = None
        projectile.tank = tank
        projectile.save()
    return tank


def truncate_trailing_zeroes(value, round_to=18):
    precision = f'%.{round_to}f' if round_to else f'%.18f'
    return (precision % value).rstrip('0').rstrip('.')
