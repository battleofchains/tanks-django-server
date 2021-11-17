import socketio


sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)


class ChatNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ):
        user = environ.get('asgi.scope', {}).get('user')
        if user.is_anonymous:
            await self.disconnect(sid)
        else:
            await self.emit('info', {'data': 'Connected'}, room=sid)
            from .async_db_calls import get_a_room, add_user_to_room, get_room_user_names
            room = await get_a_room()
            async with self.session(sid) as session:
                session['user'] = user
                session['room'] = room
            self.enter_room(sid, room.name)
            await add_user_to_room(room, user)
            users = await get_room_user_names(room)
            await self.emit('info',
                            {'data': f'{sid} Entered room: {room.name}', 'users': users},
                            room=room.name)

    async def on_disconnect(self, sid):
        async with self.session(sid) as session:
            room = session['room']
            user = session['user']
        self.leave_room(sid, room.name)
        from .async_db_calls import remove_user_from_room
        await remove_user_from_room(room, user)
        await self.emit('info', {'data': f'{sid} Left room: {room.name}'}, room=room.name)
        await self.disconnect(sid)

    async def on_broadcast_event(self, sid, message):
        await self.emit('message', {'data': message['data']})

    async def on_room_event(self, sid, message):
        await self.emit('message', {'data': message['data']}, room=message['room'])


sio.register_namespace(ChatNamespace('/chat'))
