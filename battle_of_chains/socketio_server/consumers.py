import asyncio
import random

import socketio

from .async_db_calls import (
    add_user_to_room,
    cache_get_async,
    cache_set_async,
    get_a_room,
    get_battle_types,
    get_room_user_names,
    get_user_squads,
    remove_user_from_room,
    set_battle_status,
    set_battle_winner,
)

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
        room, battle, battle_type, map_ = await get_a_room(message['battle_type'])
        async with self.session(sid) as session:
            user = session['user']
            session['room'] = room
            squad = session['squad']
        self.enter_room(sid, room.name)
        await add_user_to_room(room, user)
        users = await get_room_user_names(room)
        await self.emit('joined',
                        {'sid': sid, 'username': user.username, 'users': users, 'squad': squad, 'map': map_},
                        room=room.name)
        async with self.session(sid) as session:
            session['battle_id'] = battle.id
        if len(users) == battle_type.players_number:
            random.shuffle(users)
            order = users
            current_player = order[0]
            await cache_set_async(f'battle_{battle.id}',
                                  {'battle': battle, 'order': order,
                                   'current_player': current_player, 'state': 'running'}, 60*60)
            for i in range(5, 0, -1):
                await asyncio.sleep(1)
                await self.emit('start', {'t_minus': i}, room=room.name)
            await set_battle_status(battle, 'running')
            await self.wait_next_move(current_player, room, battle.id)

    async def on_move(self, sid, message):
        async with self.session(sid) as session:
            room = session['room']
            battle_id = session['battle_id']
            user = session['user']
        battle_data = await cache_get_async(f'battle_{battle_id}')
        if battle_data['current_player'] == user.username:
            await self.emit('move', message, room=room.name)
            battle_data = self.set_next_player(battle_data)
            await cache_set_async(f'battle_{battle_id}', battle_data, 60 * 60)

    async def on_lose(self, sid, message):
        async with self.session(sid) as session:
            user = session['user']
            room = session.get('room')
            battle_id = session.get('battle_id')
        battle_data = await cache_get_async(f'battle_{battle_id}')
        await self.emit('lose', message, room=room.name)
        looser = user.username
        order = battle_data['order']
        order.pop(order.index(looser))
        battle_data['order'] = order
        await cache_set_async(f'battle_{battle_id}', battle_data, 60 * 60)
        if len(order) == 1:
            await self.finish_game(battle_data, room)

    async def on_disconnect(self, sid):
        async with self.session(sid) as session:
            room = session.get('room')
            user = session['user']
            battle_id = session.get('battle_id')
        if room:
            self.leave_room(sid, room.name)
            await remove_user_from_room(room, user)
            users = await get_room_user_names(room)
            await self.emit('left', {'sid': sid, 'username': user.username, 'users': users}, room=room.name)
            if battle_id:
                battle_data = await cache_get_async(f'battle_{battle_id}')
                order = battle_data['order']
                order.pop(order.index(user.username))
                battle_data['order'] = order
                if battle_data['state'] == 'running' and len(users) == 1:
                    await self.finish_game(battle_data, room)
        await self.disconnect(sid)

    async def on_room_message(self, sid, message):
        async with self.session(sid) as session:
            room = session['room']
            user = session['user']
        await self.emit('room_message', {'text': message['text'], 'from': user.username}, room=room.name)

    async def wait_next_move(self, current_player, room, battle_id):
        await asyncio.sleep(2)
        for i in range(30, 0, -1):
            await asyncio.sleep(1)
            battle_data = await cache_get_async(f'battle_{battle_id}')
            if battle_data['state'] == 'running':
                if battle_data['current_player'] == current_player:
                    await self.emit('make_move', {'current_player': current_player, 't_minus': i}, room=room.name)
                else:
                    return await self.wait_next_move(battle_data['current_player'], room, battle_id)
        battle_data = await cache_get_async(f'battle_{battle_id}')
        if battle_data['current_player'] == current_player and battle_data['state'] == 'running':
            battle_data = self.set_next_player(battle_data)
            await cache_set_async(f'battle_{battle_id}', battle_data, 60 * 60)
            await self.wait_next_move(battle_data['current_player'], room, battle_id)

    async def finish_game(self, battle_data, room):
        await set_battle_status(battle_data['battle'], 'finished')
        winner = battle_data['order'][0]
        await set_battle_winner(battle_data['battle'], winner)
        battle_data['state'] = 'finished'
        await cache_set_async(f"battle_{battle_data['battle'].id}", battle_data, 60 * 60)
        await self.emit('win', {'winner': winner}, room=room.name)

    @staticmethod
    def set_next_player(battle_data):
        cur_index = battle_data['order'].index(battle_data['current_player'])
        current_player = battle_data['order'][cur_index - 1]
        battle_data['current_player'] = current_player
        return battle_data


sio.register_namespace(MainNamespace('/'))
