import random

from channels.db import database_sync_to_async
from django.core.cache import cache
from django.db.models import Count


@database_sync_to_async
def get_battle_types():
    from battle_of_chains.battle.models import BattleType
    in_cache = cache.get('battle_types')
    if in_cache:
        return in_cache
    types = tuple(BattleType.objects.all())
    cache.set('battle_types', types, 60*60*24)
    return types


@database_sync_to_async
def get_a_room(battle_type):
    from .models import Room
    available_rooms = Room.objects.annotate(users_count=Count('users'))\
        .filter(users_count__lt=4, battle_type__name=battle_type)
    if available_rooms.count() == 0:
        return Room.objects.create(battle_type_id=battle_type)
    return available_rooms.first()


@database_sync_to_async
def add_user_to_room(room, user):
    room.users.add(user)


@database_sync_to_async
def remove_user_from_room(room, user):
    room.users.remove(user)


@database_sync_to_async
def get_room_user_names(room):
    return list(room.users.values_list('username', flat=True))


@database_sync_to_async
def create_battle(room):
    from battle_of_chains.battle.models import Battle, Map
    map_ = random.choice(Map.objects.all())
    battle = Battle.objects.create(map=map_, type=room.battle_type, players=room.users.all())
    return battle
