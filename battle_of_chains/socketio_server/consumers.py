import socketio

from .async_db_calls import add_user_to_room, get_a_room, get_room_user_names, remove_user_from_room

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)


class MainNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ):
        user = environ.get('asgi.scope', {}).get('user')
        if user.is_anonymous:
            await self.disconnect(sid)
        else:
            room = await get_a_room()
            async with self.session(sid) as session:
                session['user'] = user
                session['room'] = room
            self.enter_room(sid, room.name)
            await add_user_to_room(room, user)
            users = await get_room_user_names(room)
            await self.emit('joined', {'sid': sid, 'username': user.username, 'users': users}, room=room.name)

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
