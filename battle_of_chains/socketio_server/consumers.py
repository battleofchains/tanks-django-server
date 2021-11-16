import socketio


sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)


class MyCustomNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ):
        user = environ.get('asgi.scope', {}).get('user')
        print("sid", sid)
        print(user)
        if user.is_anonymous:
            await self.disconnect(sid)
        else:
            print(self.server.manager.rooms)
            async with self.session(sid) as session:
                session['user'] = user
            await self.emit('my response', {'data': 'Connected', 'count': 0}, room=sid)

    async def on_disconnect(self, sid):
        await self.disconnect(sid)

    async def on_broadcast_event(self, sid, data):
        await self.emit('my response', {'data': data['data']})

    async def on_join(self, sid, message):
        self.enter_room(sid, message['room'])
        print(self.server.manager.rooms['/test'][message['room']])
        await self.emit('my response', {'data': 'Entered room: ' + message['room']}, room=sid)

    async def on_leave(self, sid, message):
        self.leave_room(sid, message['room'])
        await self.emit('my response', {'data': 'Left room: ' + message['room']}, room=sid)

    async def on_close_room(self, sid, message):
        await self.emit('my response', {'data': 'Room ' + message['room'] + ' is closing.'}, room=message['room'])
        await self.close_room(message['room'])

    async def on_room_event(self, sid, message):
        await self.emit('my response', {'data': message['data']}, room=message['room'])


sio.register_namespace(MyCustomNamespace('/test'))
