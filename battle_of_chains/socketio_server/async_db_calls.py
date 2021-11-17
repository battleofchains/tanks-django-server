from .models import Room
from channels.db import database_sync_to_async
from django.db.models import Count


@database_sync_to_async
def get_a_room():
    available_rooms = Room.objects.annotate(users_count=Count('users')).filter(users_count__lt=4)
    if available_rooms.count() == 0:
        return Room.objects.create()
    return available_rooms.first()


@database_sync_to_async
def add_user_to_room(room, user):
    room.users.add(user)


@database_sync_to_async
def remove_user_from_room(room, user):
    room.users.remove(user)


@database_sync_to_async
def get_room_user_names(room):
    return list(room.users.values_list('name', flat=True))
