import asyncio
import json
import logging
import time
import traceback
from functools import wraps

import socketio

from .async_db_calls import (
    clear_room,
    get_a_room,
    get_battle_types,
    get_user_tanks,
    set_battle_status,
    set_battle_winner,
)
from .game import Game

logger = logging.getLogger(__name__)

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[])
app = socketio.ASGIApp(sio)

TIME_TO_MOVE = 30


def log_and_emit_error(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        self = args[0]
        sid = args[1]
        try:
            return await function(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            logger.error(json.dumps({'func': function.__name__, 'err': str(e), 'traceback': tb}))
            await self.emit('error', {'error': str(e), 'traceback': tb}, room=sid)
            raise e
    return wrapper


def log_json_info(**kwargs):
    logger.info(json.dumps(kwargs))


class MainNamespace(socketio.AsyncNamespace):

    def __init__(self, namespace=None):
        self.games = {}
        super(MainNamespace, self).__init__(namespace=namespace)

    @log_and_emit_error
    async def on_connect(self, sid, environ):
        user = environ.get('asgi.scope', {}).get('user')
        log_json_info(event_source="client", event="connect", sid=sid, user_id=user.id or 0)
        if user.is_anonymous:
            await self.disconnect(sid)
        else:
            async with self.session(sid) as session:
                session['user'] = user
            battle_types = await get_battle_types()
            msg = {'battle_types': battle_types}
            await self.emit('select_battle', msg, room=sid)
            log_json_info(event_source='server', event='select_battle', sid=sid, user_id=user.id, msg=msg)

    @log_and_emit_error
    async def on_select_battle(self, sid, message):
        async with self.session(sid) as session:
            user = session['user']
            session['battle_type'] = message['battle_type']
        log_json_info(event_source='client', event='select_battle', sid=sid, user_id=user.id, msg=message)
        tanks = await get_user_tanks(user)
        msg = {'tanks': tanks}
        await self.emit('select_tanks', msg, room=sid)
        log_json_info(event_source='server', event='select_tanks', sid=sid, user_id=user.id, msg=msg)

    @log_and_emit_error
    async def on_select_tanks(self, sid, message):
        async with self.session(sid) as session:
            user = session['user']
            battle_type = session['battle_type']
        log_json_info(event_source='client', event='select_tanks', sid=sid, user_id=user.id, msg=message)
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

        msg = {'sid': sid, 'username': user.username, 'users_data': game.users, 'map': map_, 'usernames': usernames}
        await self.emit('joined', msg, room=room.name)
        log_json_info(event_source='server', event='joined', sid=sid,
                      user_id=user.id, msg=msg, room=room.name, battle=battle.id)
        async with self.session(sid) as session:
            session['game_id'] = game.id
        if len(usernames) == battle_type.players_number:
            await game.start()
            for i in range(5, 0, -1):
                await asyncio.sleep(1)
                await self.emit('start', {'t_minus': i}, room=room.name)
                log_json_info(event_source='server', event='start', sid=sid,
                              user_id=user.id, msg={'t_minus': i}, room=room.name, battle=battle.id)
            await set_battle_status(battle, 'running')
            await self.wait_next_move(game, game.current_player)

    @log_and_emit_error
    async def on_move(self, sid, message):
        async with self.session(sid) as session:
            game_id = session['game_id']
            user = session['user']
        game = self.games.get(game_id)
        log_json_info(event_source='client', event='move', sid=sid, user_id=user.id,
                      msg=message, room=game.room.name, battle=game.battle.id)
        if game.current_player['username'] == user.username:
            await self.emit('move', message, room=game.room.name)
            log_json_info(event_source='server', event='move', sid=sid, user_id=user.id,
                          msg=message, room=game.room.name, battle=game.battle.id)

    @log_and_emit_error
    async def on_shoot(self, sid, message):
        async with self.session(sid) as session:
            game_id = session['game_id']
            user = session['user']
        game = self.games.get(game_id)
        log_json_info(event_source='client', event='shoot', sid=sid, user_id=user.id,
                      msg=message, room=game.room.name, battle=game.battle.id)
        if game.current_player['username'] == user.username:
            await self.emit('shoot', message, room=game.room.name)
            log_json_info(event_source='server', event='shoot', sid=sid, user_id=user.id,
                          msg=message, room=game.room.name, battle=game.battle.id)

    @log_and_emit_error
    async def on_turn(self, sid, message):
        async with self.session(sid) as session:
            game_id = session['game_id']
            user = session['user']
        game = self.games.get(game_id)
        log_json_info(event_source='client', event='turn', sid=sid, user_id=user.id,
                      msg=message, room=game.room.name, battle=game.battle.id)
        if game.current_player['username'] == user.username:
            await self.emit('turn', message, room=game.room.name)
            log_json_info(event_source='server', event='turn', sid=sid, user_id=user.id,
                          msg=message, room=game.room.name, battle=game.battle.id)
            self.set_next_player(game)

    @log_and_emit_error
    async def on_lose(self, sid, message):
        async with self.session(sid) as session:
            user = session['user']
            game_id = session.get('game_id')
        game = self.games.get(game_id)
        log_json_info(event_source='client', event='lose', sid=sid, user_id=user.id,
                      msg=message, room=game.room.name, battle=game.battle.id)
        await self.emit('lose', message, room=game.room.name)
        log_json_info(event_source='server', event='lose', sid=sid, user_id=user.id,
                      msg=message, room=game.room.name, battle=game.battle.id)
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
        log_json_info(event_source='client', event='disconnect', sid=sid, user_id=user.id if user else 0)
        if game:
            self.leave_room(sid, game.room.name)
            await game.remove_user(user)
            usernames = list(game.users.keys())
            message = {'sid': sid, 'username': user.username, 'usernames': usernames}
            await self.emit('left', message, room=game.room.name)
            log_json_info(event_source='server', event='left', sid=sid, user_id=user.id,
                          msg=message, room=game.room.name, battle=game.battle.id)
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
        log_json_info(event_source='client', event='room_message', sid=sid, user_id=user.id,
                      msg=message, room=game.room.name, battle=game.battle.id)
        await self.emit('room_message', {'text': message['text'], 'from': user.username}, room=game.room.name)
        log_json_info(event_source='server', event='room_message', sid=sid, user_id=user.id,
                      msg=message, room=game.room.name, battle=game.battle.id)

    async def wait_next_move(self, game, current_player):
        player = current_player['username']
        for i in range(TIME_TO_MOVE, 0, -1):
            await asyncio.sleep(1)
            if game.state == 'running':
                if game.current_player['username'] == player:
                    message = {'current_player': current_player, 't_minus': i}
                    await self.emit('make_move', message, room=game.room.name)
                    log_json_info(event_source='server', event='make_move', msg=message,
                                  room=game.room.name, battle=game.battle.id)
                else:
                    return await self.wait_next_move(game, game.current_player)
        if game.current_player['username'] == player and game.state == 'running':
            await self.emit('turn', {"username": player}, room=game.room.name)
            log_json_info(event_source='server', event='turn', msg={"username": player},
                          room=game.room.name, battle=game.battle.id)
            self.set_next_player(game)
            await self.wait_next_move(game, game.current_player)

    async def finish_game(self, game):
        await set_battle_status(game.battle, 'finished')
        winner = game.order[0]
        duration = time.time() - game.started
        await set_battle_winner(game.battle, winner, duration)
        game.state = Game.STATE.FINISHED
        await self.emit('win', {'winner': winner}, room=game.room.name)
        log_json_info(event_source='server', event='win', msg={'winner': winner},
                      room=game.room.name, battle=game.battle.id)
        await self.close_room(game.room.name)
        for u in list(game.users.values()):
            await self.disconnect(u['sid'])
        await clear_room(game.room)
        try:
            del self.games[game.id]
        except KeyError:
            pass

    @staticmethod
    def set_next_player(game):
        cur_index = game.order.index(game.current_player['username'])
        current_player = game.order[cur_index - 1]
        tanks_order = game.users[current_player]['tanks_order']
        last_tank = game.users[current_player].get('last_tank')
        if last_tank:
            cur_tank_index = tanks_order.index(last_tank)
            current_tank = tanks_order[cur_tank_index - 1]
        else:
            current_tank = tanks_order[-1]
        game.users[current_player]['last_tank'] = current_tank
        game.current_player = {'username': current_player, 'tank': current_tank}


sio.register_namespace(MainNamespace('/'))
