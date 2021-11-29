import asyncio
import random
import traceback
from functools import wraps

import socketio
from loguru import logger

from .async_db_calls import (
    clear_room,
    get_a_room,
    get_battle_types,
    get_user_tanks,
    set_battle_status,
    set_battle_winner,
)
from .game import Game

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[])
app = socketio.ASGIApp(sio)


def log_and_emit_error(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        self = args[0]
        sid = args[1]
        try:
            return await function(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            err = f"Exception in {function.__name__}. Error: {e}. Traceback: {tb}"
            logger.error(err)
            await self.emit('error', {'error': str(e), 'traceback': tb}, room=sid)
            raise e
    return wrapper


class MainNamespace(socketio.AsyncNamespace):

    def __init__(self, namespace=None):
        self.games = {}
        super(MainNamespace, self).__init__(namespace=namespace)

    @log_and_emit_error
    async def on_connect(self, sid, environ):
        user = environ.get('asgi.scope', {}).get('user')
        if user.is_anonymous:
            await self.disconnect(sid)
        else:
            async with self.session(sid) as session:
                session['user'] = user
            battle_types = await get_battle_types()
            await self.emit('select_battle', {'battle_types': battle_types}, room=sid)

    @log_and_emit_error
    async def on_select_battle(self, sid, message):
        async with self.session(sid) as session:
            user = session['user']
            session['battle_type'] = message['battle_type']
        tanks = await get_user_tanks(user)
        await self.emit('select_tanks', {'tanks': tanks}, room=sid)

    @log_and_emit_error
    async def on_select_tanks(self, sid, message):
        async with self.session(sid) as session:
            user = session['user']
            battle_type = session['battle_type']
        room, battle, battle_type, map_ = await get_a_room(battle_type)
        tanks = message['tanks'][:battle_type.player_tanks_number]
        self.enter_room(sid, room.name)
        game_id = f'{room.id}_{battle.id}'
        if self.games.get(game_id):
            game = self.games[game_id]
        else:
            game = Game(room, battle)
            self.games[game.id] = game
        await game.add_user(user, sid, tanks)
        usernames = list(game.users.keys())

        await self.emit(
            'joined',
            {'sid': sid, 'username': user.username, 'users': game.users, 'map': map_},
            room=room.name
        )
        async with self.session(sid) as session:
            session['game_id'] = game.id
        if len(usernames) == battle_type.players_number:
            random.shuffle(usernames)
            game.order = usernames
            game.current_player = game.order[0]
            game.state = game.STATE.RUNNING
            for i in range(5, 0, -1):
                await asyncio.sleep(1)
                await self.emit('start', {'t_minus': i}, room=room.name)
            await set_battle_status(battle, 'running')
            await self.wait_next_move(game, game.current_player)

    @log_and_emit_error
    async def on_move(self, sid, message):
        async with self.session(sid) as session:
            game_id = session['game_id']
            user = session['user']
        game = self.games.get(game_id)
        if game.current_player == user.username:
            await self.emit('move', message, room=game.room.name)

    @log_and_emit_error
    async def on_shoot(self, sid, message):
        async with self.session(sid) as session:
            game_id = session['game_id']
            user = session['user']
        game = self.games.get(game_id)
        if game.current_player == user.username:
            await self.emit('shoot', message, room=game.room.name)

    @log_and_emit_error
    async def on_turn(self, sid, message):
        async with self.session(sid) as session:
            game_id = session['game_id']
            user = session['user']
        game = self.games.get(game_id)
        if game.current_player == user.username:
            await self.emit('turn', message, room=game.room.name)
            self.set_next_player(game)

    @log_and_emit_error
    async def on_lose(self, sid, message):
        async with self.session(sid) as session:
            user = session['user']
            game_id = session.get('game_id')
        game = self.games.get(game_id)
        await self.emit('lose', message, room=game.room.name)
        looser = user.username
        game.order.pop(game.order.index(looser))
        if len(game.order) == 1:
            await self.finish_game(game)

    @log_and_emit_error
    async def on_disconnect(self, sid):
        async with self.session(sid) as session:
            user = session.get('user')
            game_id = session.get('game_id')
        game = self.games.get(game_id)
        if game:
            self.leave_room(sid, game.room.name)
            await game.remove_user(user)
            usernames = list(game.users.keys())
            await self.emit('left', {'sid': sid, 'username': user.username, 'users': usernames}, room=game.room.name)
            if game.order:
                game.order.pop(game.order.index(user.username))
            if game.state == Game.STATE.RUNNING and len(usernames) == 1:
                await self.finish_game(game)
        await self.disconnect(sid)

    @log_and_emit_error
    async def on_room_message(self, sid, message):
        async with self.session(sid) as session:
            game_id = session['game_id']
            user = session['user']
        game = self.games.get(game_id)
        await self.emit('room_message', {'text': message['text'], 'from': user.username}, room=game.room.name)

    async def wait_next_move(self, game, current_player):
        player = current_player
        await asyncio.sleep(1)
        for i in range(30, 0, -1):
            await asyncio.sleep(1)
            if game.state == 'running':
                if game.current_player == player:
                    await self.emit('make_move', {'current_player': current_player, 't_minus': i}, room=room.name)
                else:
                    return await self.wait_next_move(game, game.current_player)
        if game.current_player == player and game.state == 'running':
            self.set_next_player(game)
            await self.wait_next_move(game, game.current_player)

    async def finish_game(self, game):
        await set_battle_status(game.battle, 'finished')
        winner = game.order[0]
        await set_battle_winner(game.battle, winner)
        game.state = Game.STATE.FINISHED
        await self.emit('win', {'winner': winner}, room=game.room.name)
        await self.close_room(game.room.name)
        for u in game.users.values():
            await self.disconnect(u['sid'])
        await clear_room(game.room)

    @staticmethod
    def set_next_player(game):
        cur_index = game.order.index(game.current_player)
        current_player = game.order[cur_index - 1]
        game.current_player = current_player


sio.register_namespace(MainNamespace('/'))
