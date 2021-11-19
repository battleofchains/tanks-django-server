import asyncio
import random

import socketio

from .async_db_calls import (
    add_user_to_room,
    create_battle,
    get_a_room,
    get_battle_types,
    get_room_user_names,
    remove_user_from_room,
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
            battle_types = await get_battle_types()
            await self.emit('select_battle', {'battle_types': [bt.name for bt in battle_types]}, room=sid)

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
            random.shuffle(users)
            battle.order = users
            current_player = battle.order[0]
            battle.current_player = current_player
            for i in range(5, 0, -1):
                await asyncio.sleep(1)
                await self.emit('start', {'left': i}, room=room.name)
            await self.emit('make_move', {'current_player': current_player}, room=room.name)

    async def on_move(self, sid, message):
        async with self.session(sid) as session:
            user = session['user']
            room = session['room']
        await self.emit('move', {'player': user, 'data': message}, room=room.name)

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


sio.register_namespace(MainNamespace('/'))
