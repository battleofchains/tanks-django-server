import random

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count

from battle_of_chains.battle.models import Battle, BattleType, Map, Squad
from battle_of_chains.battle.serializers import (
    BattleTypeSerializer,
    MapSerializer,
    TankSerializer,
)

from .models import Room

User = get_user_model()


@database_sync_to_async
def get_battle_types():
    in_cache = cache.get('battle_types')
    if in_cache:
        return in_cache
    types = BattleTypeSerializer(BattleType.objects.all(), many=True).data
    cache.set('battle_types', types, 60*60*24)
    return types


@database_sync_to_async
def get_user_tanks(user):
    return TankSerializer(Squad.objects.filter(owner=user), many=True).data


@database_sync_to_async
def get_a_room(battle_type):
    b_type = BattleType.objects.get(name=battle_type)
    available_rooms = Room.objects.annotate(users_count=Count('users'))\
        .filter(users_count__lt=b_type.players_number, battle__type=b_type,
                battle__status__in=[Battle.STATUS.WAITING, Battle.STATUS.FINISHED])
    if available_rooms.count() == 0:
        map_ = random.choice(Map.objects.all())
        battle = Battle.objects.create(map=map_, type=b_type)
        room = Room.objects.create(battle=battle)
        return room, room.battle, room.battle.type, MapSerializer(room.battle.map).data
    room = available_rooms.first()
    if room.battle.status == Battle.STATUS.FINISHED:
        map_ = random.choice(Map.objects.all())
        battle = Battle.objects.create(map=map_, type=b_type)
        room.battle = battle
        room.save()
    return room, room.battle, room.battle.type, MapSerializer(room.battle.map).data


@database_sync_to_async
def add_user_to_room(room, user):
    room.users.add(user)
    room.battle.players.add(user)


@database_sync_to_async
def remove_user_from_room(room, user):
    room.users.remove(user)


@database_sync_to_async
def clear_room(room):
    room.users.clear()


@database_sync_to_async
def get_room_user_names(room):
    return list(room.users.values_list('username', flat=True))


@database_sync_to_async
def set_battle_status(battle, status):
    battle.status = status
    battle.save(update_fields=['status'])


@database_sync_to_async
def set_battle_winner(battle, winner, duration):
    winner = User.objects.get(username=winner)
    battle.winner = winner
    battle.duration = duration
    battle.save(update_fields=['winner', 'duration'])


@sync_to_async
def cache_set_async(key, val, timeout):
    return cache.set(key, val, timeout)


@sync_to_async
def cache_get_async(key):
    return cache.get(key)
