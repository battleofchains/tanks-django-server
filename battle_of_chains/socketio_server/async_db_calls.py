import random

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.db.models import Count

from battle_of_chains.battle.serializers import BattleTypeSerializer, SquadSerializer


@database_sync_to_async
def get_battle_types():
    from battle_of_chains.battle.models import BattleType
    in_cache = cache.get('battle_types')
    if in_cache:
        return in_cache
    types = BattleTypeSerializer(BattleType.objects.all(), many=True).data
    cache.set('battle_types', types, 60*60*24)
    return types


@database_sync_to_async
def get_user_squads(user):
    from battle_of_chains.battle.models import Squad
    return SquadSerializer(Squad.objects.filter(owner=user), many=True).data


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


@database_sync_to_async
def set_battle_status(battle, status):
    battle.status = status
    battle.save(update_fields=['status'])


@database_sync_to_async
def set_battle_winner(battle, winner):
    from battle_of_chains.users.models import User
    winner = User.objects.get(username=winner)
    battle.winner = winner
    battle.save(update_fields=['winner'])


@sync_to_async
def cache_set_async(key, val, timeout):
    return cache.set(key, val, timeout)


@sync_to_async
def cache_get_async(key):
    return cache.get(key)
