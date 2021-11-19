import asyncio
import random

import socketio

from .async_db_calls import (
    add_user_to_room, cache_get_async, cache_set_async, create_battle, get_a_room, get_battle_types,
    get_room_user_names, get_user_squads, remove_user_from_room)

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)


class MainNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ):
        user = environ.get('asgi.scope', {}).get('user')
        if user.is_anonymous:
            await self.disconnect(sid)
        else:
            async with self.session(sid) as session:
                session['user'] = user
            squads = await get_user_squads(user)
            await self.emit('select_squad', {'squads': squads}, room=sid)

    async def on_select_squad(self, sid, message):
        battle_types = await get_battle_types()
        async with self.session(sid) as session:
            session['squad'] = message['squad']
        await self.emit('select_battle', {'battle_types': battle_types}, room=sid)

    async def on_select_battle(self, sid, message):
        room = await get_a_room(message['battle_type'])
        async with self.session(sid) as session:
            user = session['user']
            session['room'] = room
        self.enter_room(sid, room.name)
        await add_user_to_room(room, user)
        users = await get_room_user_names(room)
        await self.emit('joined', {'sid': sid, 'username': user.username, 'users': users}, room=room.name)
        if len(users) == room.battle_type.players_number:
            battle = await create_battle(room)
            async with self.session(sid) as session:
                session['battle_id'] = battle.id
            random.shuffle(users)
            order = users
            current_player = order[0]
            await cache_set_async(f'battle_{battle.id}',
                                  {'battle': battle, 'order': order, 'current_player': current_player}, 60*60)
            for i in range(5, 0, -1):
                await asyncio.sleep(1)
                await self.emit('start', {'left': i}, room=room.name)
            await self.wait_next_move(current_player, room, battle.id)

    async def on_move(self, sid, message):
        async with self.session(sid) as session:
            user = session['user']
            room = session['room']
            battle_id = session['battle_id']
        await self.emit('move', {'player': user, 'data': message}, room=room.name)
        battle_data = await cache_get_async(f'battle_{battle_id}')
        battle_data = self.set_next_player(battle_data)
        await cache_set_async(f'battle_{battle_id}', battle_data, 60 * 60)
        await self.wait_next_move(battle_data['current_player'], room, battle_id)

    async def on_disconnect(self, sid):
        async with self.session(sid) as session:
            room = session['room']
            user = session['user']
        self.leave_room(sid, room.name)
        await remove_user_from_room(room, user)
        users = await get_room_user_names(room)
        await self.emit('left', {'sid': sid, 'username': user.username, 'users': users}, room=room.name)
        await self.disconnect(sid)

    async def on_room_message(self, sid, message):
        async with self.session(sid) as session:
            room = session['room']
            user = session['user']
        await self.emit('room_message', {'text': message['text'], 'from': user.username}, room=room.name)

    async def wait_next_move(self, current_player, room, battle_id):
        for i in range(15, 0, -1):
            await asyncio.sleep(1)
            battle_data = await cache_get_async(f'battle_{battle_id}')
            if battle_data['current_player'] == current_player:
                await self.emit('make_move', {'current_player': current_player}, room=room.name)
            else:
                return
        battle_data = await cache_get_async(f'battle_{battle_id}')
        if battle_data['current_player'] == current_player:
            battle_data = self.set_next_player(battle_data)
            await cache_set_async(f'battle_{battle_id}', battle_data, 60 * 60)
            await self.wait_next_move(current_player, room, battle_id)

    @staticmethod
    def set_next_player(battle_data):
        cur_index = battle_data['order'].index(battle_data['current_player'])
        current_player = battle_data['order'][cur_index - 1]
        battle_data['current_player'] = current_player
        return battle_data


sio.register_namespace(MainNamespace('/'))
